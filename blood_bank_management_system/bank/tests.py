from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import BloodRequest, BloodStock, Donor, DonationAppointment, ContactRequest
from django.core import mail


class BankBasicTests(TestCase):
    def setUp(self):
        self.client = Client()
        # create a staff user
        self.staff = User.objects.create_user('staff', 'staff@example.com', 'staffpass')
        self.staff.is_staff = True
        self.staff.is_superuser = True
        self.staff.save()
        # initial stock
        BloodStock.objects.create(blood_group='A+', units=5)

    def test_home_loads(self):
        resp = self.client.get(reverse('home'))
        self.assertEqual(resp.status_code, 200)

    def test_request_creation_and_pending(self):
        data = {
            'patient_name': 'Test Patient',
            'hospital_name': 'Test Hospital',
            'contact_number': '9000000000',
            'contact_email': 'requester@example.com',
            'blood_group': 'A+',
            'units_required': 1,
            'reason': 'Testing',
        }
        resp = self.client.post(reverse('request_blood'), data, follow=True)
        self.assertEqual(resp.status_code, 200)
        br = BloodRequest.objects.get(patient_name='Test Patient')
        self.assertEqual(br.status, 'Pending')

    def test_approve_requires_staff_and_sends_email(self):
        br = BloodRequest.objects.create(
            patient_name='P', hospital_name='H', contact_number='900', contact_email='r@example.com', blood_group='A+', units_required=1
        )
        # non-staff cannot approve
        resp = self.client.get(reverse('approve_request', args=[br.id]), follow=True)
        br.refresh_from_db()
        self.assertEqual(br.status, 'Pending')
        # staff can approve
        self.client.login(username='staff', password='staffpass')
        resp = self.client.get(reverse('approve_request', args=[br.id]), follow=True)
        br.refresh_from_db()
        self.assertEqual(br.status, 'Approved')
        # an email should have been sent to contact_email
        self.assertEqual(len(mail.outbox), 1)

    def test_contact_request_flow_and_staff_approval(self):
        donor = Donor.objects.create(name='D1', age=30, gender='Male', phone='9001112222', email='d1@example.com', address='Addr', city='CityX', blood_group='A+')
        data = {
            'donor': donor.id,
            'requester_name': 'Req One',
            'requester_contact': 'req@example.com',
            'message': 'Please share contact',
        }
        resp = self.client.post(reverse('request_contact', args=[donor.id]), data, follow=True)
        self.assertEqual(resp.status_code, 200)
        from .models import ContactRequest
        cr = ContactRequest.objects.get(requester_name='Req One')
        self.assertEqual(cr.status, 'Pending')
        # staff approves
        self.client.login(username='staff', password='staffpass')
        resp = self.client.get(reverse('change_contact_request_status', args=[cr.id, 'Approved']), follow=True)
        cr.refresh_from_db()
        self.assertEqual(cr.status, 'Approved')
        # an email should have been sent (to requester) - console backend fills outbox
        self.assertGreaterEqual(len(mail.outbox), 1)

    def test_appointment_booking_and_status_change(self):
        # book appointment
        slot_str = '2026-07-10T10:00'
        data = {
            'donor_name': 'Donor Appt',
            'donor_email': 'appt@example.com',
            'donor_phone': '9002223333',
            'hospital': 'City Hospital',
            'slot': slot_str,
        }
        resp = self.client.post(reverse('book_appointment'), data, follow=True)
        self.assertEqual(resp.status_code, 200)
        appt = DonationAppointment.objects.get(donor_name='Donor Appt')
        self.assertEqual(appt.status, 'Pending')
        # non-staff cannot change
        resp = self.client.get(reverse('change_appointment_status', args=[appt.id, 'Confirmed']), follow=True)
        appt.refresh_from_db()
        self.assertEqual(appt.status, 'Pending')
        # staff can change and email should be sent
        self.client.login(username='staff', password='staffpass')
        resp = self.client.get(reverse('change_appointment_status', args=[appt.id, 'Confirmed']), follow=True)
        appt.refresh_from_db()
        self.assertEqual(appt.status, 'Confirmed')
        self.assertGreaterEqual(len(mail.outbox), 1)

    def test_export_donors_csv_and_audit_log(self):
        # create donors
        Donor.objects.create(name='ExportMe', age=40, gender='Male', phone='9000001111', email='ex@example.com', address='Addr', city='Xcity', blood_group='O+')
        # non-staff cannot export: should be redirected
        resp = self.client.get(reverse('export_donors_csv'), follow=True)
        self.assertTrue(resp.redirect_chain)
        # staff can export
        self.client.login(username='staff', password='staffpass')
        resp = self.client.get(reverse('export_donors_csv'))
        self.assertEqual(resp.status_code, 200)
        self.assertIn('text/csv', resp['Content-Type'])
        content = resp.content.decode()
        self.assertIn('ExportMe', content)

    def test_audit_log_created_for_actions(self):
        from .models import AuditLog
        # perform an action: accept a donor application
        app = Donor.objects.create(name='AuditDonor', age=29, gender='Male', phone='900', email='a@example.com', address='Addr', city='C', blood_group='A+')
        # staff changes something: change appointment status
        appt = DonationAppointment.objects.create(donor_name='A', donor_email='a@b.com', donor_phone='900', hospital='H', slot='2026-07-10T10:00')
        self.client.login(username='staff', password='staffpass')
        resp = self.client.get(reverse('change_appointment_status', args=[appt.id, 'Confirmed']), follow=True)
        self.assertEqual(resp.status_code, 200)
        logs = AuditLog.objects.filter(action__icontains=f'Changed appointment {appt.id}')
        self.assertTrue(logs.exists())
