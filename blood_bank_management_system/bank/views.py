from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.core.mail import send_mail
from django.conf import settings
from .forms import DonorForm, BloodStockForm, BloodRequestForm
from .models import Donor, BloodStock, BloodRequest
from .forms import DonorApplicationForm, DonationAppointmentForm
from .models import DonorApplication, DonationAppointment
from .models import ContactRequest, AuditLog
from .forms import ContactRequestForm
from django.core.paginator import Paginator
from django.http import HttpResponse
import csv
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from .forms import UserRegistrationForm


def home(request):
    total_donors = Donor.objects.count()
    total_units = sum(stock.units for stock in BloodStock.objects.all())
    pending_requests = BloodRequest.objects.filter(status='Pending').count()
    stocks = BloodStock.objects.all().order_by('blood_group')
    return render(request, 'bank/home.html', {
        'total_donors': total_donors,
        'total_units': total_units,
        'pending_requests': pending_requests,
        'stocks': stocks,
    })


def add_donor(request):
    # Only staff should add donors directly. Non-staff are redirected to the donor application.
    if not request.user.is_staff:
        messages.info(request, 'Please apply to become a donor; staff can add donors.')
        return redirect('apply_donor')
    if request.method == 'POST':
        form = DonorForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Donor registered successfully!')
            return redirect('donor_list')
    else:
        form = DonorForm()
    return render(request, 'bank/form.html', {'form': form, 'title': 'Register Donor (Staff)'})


def donor_list(request):
    blood_group = request.GET.get('blood_group')
    city = request.GET.get('city')
    hospital = request.GET.get('hospital')
    donors = Donor.objects.all().order_by('-created_at')
    if blood_group:
        donors = donors.filter(blood_group=blood_group)
    if city:
        donors = donors.filter(city__icontains=city)
    if hospital:
        # match hospital text in address (best-effort)
        donors = donors.filter(address__icontains=hospital)
    # paginate
    paginator = Paginator(donors, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'bank/donor_list.html', {'donors': page_obj, 'selected_group': blood_group, 'selected_city': city, 'selected_hospital': hospital, 'page_obj': page_obj})


def apply_donor(request):
    if request.method == 'POST':
        form = DonorApplicationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Application submitted. Our staff will review it.')
            return redirect('home')
    else:
        form = DonorApplicationForm()
    return render(request, 'bank/form.html', {'form': form, 'title': 'Apply to be a Donor'})


def application_list(request):
    if not request.user.is_staff:
        messages.error(request, 'Only staff can view donor applications.')
        return redirect('home')
    apps = DonorApplication.objects.all().order_by('-applied_at')
    return render(request, 'bank/application_list.html', {'applications': apps})


def accept_application(request, app_id):
    if not request.user.is_staff:
        messages.error(request, 'Only staff can accept applications.')
        return redirect('application_list')
    app = get_object_or_404(DonorApplication, id=app_id)
    donor = Donor.objects.create(
        name=app.name,
        age=app.age,
        gender=app.gender,
        phone=app.phone,
        email=app.email,
        address=app.address,
        blood_group=app.blood_group,
        last_donation_date=app.last_donation_date,
    )
    app.status = 'Approved'
    app.save()
    messages.success(request, f'Application accepted and donor {donor.name} created.')
    return redirect('application_list')


def add_donor_staff(request):
    if not request.user.is_staff:
        messages.error(request, 'Only staff can add donors.')
        return redirect('donor_list')
    if request.method == 'POST':
        form = DonorForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Donor added successfully.')
            return redirect('donor_list')
    else:
        form = DonorForm()
    return render(request, 'bank/form.html', {'form': form, 'title': 'Add Donor (Staff)'})


def book_appointment(request):
    if request.method == 'POST':
        form = DonationAppointmentForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            DonationAppointment.objects.create(
                donor_name=data['donor_name'],
                donor_email=data.get('donor_email',''),
                donor_phone=data.get('donor_phone',''),
                hospital=data.get('hospital',''),
                slot=data['slot'],
            )
            messages.success(request, 'Appointment requested. Staff will confirm shortly.')
            return redirect('home')
    else:
        form = DonationAppointmentForm()
    return render(request, 'bank/form.html', {'form': form, 'title': 'Book Donation Appointment'})


def appointment_list(request):
    if not request.user.is_staff:
        messages.error(request, 'Only staff can view appointments.')
        return redirect('home')
    appts = DonationAppointment.objects.all().order_by('slot')
    return render(request, 'bank/appointment_list.html', {'appointments': appts})


def change_appointment_status(request, appt_id, status):
    if not request.user.is_staff:
        messages.error(request, 'Only staff can change appointment status.')
        return redirect('appointment_list')
    appt = get_object_or_404(DonationAppointment, id=appt_id)
    if status not in dict(DonationAppointment.APPT_STATUS):
        messages.error(request, 'Invalid status')
        return redirect('appointment_list')
    appt.status = status
    appt.save()
    # log action
    AuditLog.objects.create(actor=request.user, action=f'Changed appointment {appt.id} status to {status}', target=str(appt))
    # notify donor if email available
    if appt.donor_email:
        try:
            send_mail(f'Appointment {status}', f'Your appointment is now {status}.', settings.DEFAULT_FROM_EMAIL, [appt.donor_email])
        except Exception:
            pass
    messages.success(request, f'Appointment {status}.')
    return redirect('appointment_list')


def request_contact(request, donor_id=None):
    if request.method == 'POST':
        form = ContactRequestForm(request.POST)
        if form.is_valid():
            cr = form.save()
            messages.success(request, 'Contact request submitted. Staff will review.')
            return redirect('donor_list')
    else:
        initial = {}
        if donor_id:
            initial['donor'] = donor_id
        form = ContactRequestForm(initial=initial)
    return render(request, 'bank/form.html', {'form': form, 'title': 'Request Donor Contact'})


def contact_requests_list(request):
    if not request.user.is_staff:
        messages.error(request, 'Only staff can view contact requests.')
        return redirect('home')
    qs = ContactRequest.objects.all().order_by('-created_at')
    return render(request, 'bank/contact_requests.html', {'requests': qs})


def change_contact_request_status(request, req_id, status):
    if not request.user.is_staff:
        messages.error(request, 'Only staff can change request status.')
        return redirect('contact_requests')
    cr = get_object_or_404(ContactRequest, id=req_id)
    if status not in dict(ContactRequest.STATUS):
        messages.error(request, 'Invalid status')
        return redirect('contact_requests')
    cr.status = status
    cr.save()
    AuditLog.objects.create(actor=request.user, action=f'Changed contact request {cr.id} status to {status}', target=str(cr))
    # notify requester via contact info (best-effort via email)
    if cr.requester_contact and '@' in cr.requester_contact and status == 'Approved':
        try:
            send_mail('Contact Request Approved', f'The donor contact details: {cr.donor.phone} / {cr.donor.email}', settings.DEFAULT_FROM_EMAIL, [cr.requester_contact])
        except Exception:
            pass
    messages.success(request, f'Request {status}.')
    return redirect('contact_requests')


def export_donors_csv(request):
    if not request.user.is_staff:
        messages.error(request, 'Only staff can export data.')
        return redirect('donor_list')
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="donors.csv"'
    writer = csv.writer(response)
    writer.writerow(['name','age','gender','phone','email','city','blood_group','last_donation_date'])
    for d in Donor.objects.all():
        writer.writerow([d.name,d.age,d.gender,d.phone,d.email,d.city,d.blood_group,d.last_donation_date])
    return response


def user_register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful. You are logged in.')
            return redirect('home')
    else:
        form = UserRegistrationForm()
    return render(request, 'bank/register.html', {'form': form, 'title': 'Register'})


def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, 'Logged in successfully.')
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'bank/login.html', {'form': form, 'title': 'Login'})


def staff_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if user.is_staff:
                login(request, user)
                messages.success(request, 'Staff login successful.')
                return redirect('application_list')
            else:
                messages.error(request, 'Not a staff account.')
    else:
        form = AuthenticationForm()
    return render(request, 'bank/staff_login.html', {'form': form, 'title': 'Staff Login'})


def user_logout(request):
    logout(request)
    messages.info(request, 'Logged out.')
    return redirect('home')


def add_stock(request):
    if not request.user.is_staff:
        messages.error(request, 'Only staff can add or update stock.')
        return redirect('home')

    if request.method == 'POST':
        form = BloodStockForm(request.POST)
        if form.is_valid():
            blood_group = form.cleaned_data['blood_group']
            units = form.cleaned_data['units']
            stock, created = BloodStock.objects.get_or_create(blood_group=blood_group)
            stock.units += units
            stock.save()
            messages.success(request, 'Blood stock updated successfully!')
            return redirect('stock_list')
    else:
        form = BloodStockForm()
    return render(request, 'bank/form.html', {'form': form, 'title': 'Add Blood Stock'})


def stock_list(request):
    stocks = BloodStock.objects.all().order_by('blood_group')
    return render(request, 'bank/stock_list.html', {'stocks': stocks})


def request_blood(request):
    if request.method == 'POST':
        form = BloodRequestForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Blood request submitted successfully!')
            return redirect('request_list')
    else:
        form = BloodRequestForm()
    return render(request, 'bank/form.html', {'form': form, 'title': 'Request Blood'})


def request_list(request):
    # Only staff should see the full list of requests; public users can view their own requests via other pages.
    if not request.user.is_staff:
        messages.error(request, 'Only staff can view all blood requests.')
        return redirect('home')
    requests = BloodRequest.objects.all().order_by('-request_date')
    return render(request, 'bank/request_list.html', {'requests': requests})


def approve_request(request, request_id):
    blood_request = get_object_or_404(BloodRequest, id=request_id)
    if not request.user.is_staff:
        messages.error(request, 'Only staff or management can approve requests.')
        return redirect('request_list')
    stock = BloodStock.objects.filter(blood_group=blood_request.blood_group).first()
    if stock and stock.units >= blood_request.units_required:
        stock.units -= blood_request.units_required
        stock.save()
        blood_request.status = 'Approved'
        blood_request.notification = f"Your request for {blood_request.units_required} unit(s) of {blood_request.blood_group} has been approved. Please contact the hospital: {blood_request.hospital_name}."
        # send email notification if contact_email provided
        if blood_request.contact_email:
            subject = 'Blood Request Approved'
            message = blood_request.notification
            from_email = settings.DEFAULT_FROM_EMAIL
            try:
                send_mail(subject, message, from_email, [blood_request.contact_email])
            except Exception:
                pass
        blood_request.save()
        messages.success(request, 'Request approved and stock updated!')
    else:
        messages.error(request, 'Not enough blood stock available.')
    return redirect('request_list')


def reject_request(request, request_id):
    blood_request = get_object_or_404(BloodRequest, id=request_id)
    if not request.user.is_staff:
        messages.error(request, 'Only staff or management can reject requests.')
        return redirect('request_list')
    blood_request.status = 'Rejected'
    blood_request.notification = f"Your request for {blood_request.units_required} unit(s) of {blood_request.blood_group} has been rejected. Please contact the hospital for more details."
    if blood_request.contact_email:
        subject = 'Blood Request Rejected'
        message = blood_request.notification
        from_email = settings.DEFAULT_FROM_EMAIL
        try:
            send_mail(subject, message, from_email, [blood_request.contact_email])
        except Exception:
            pass
    blood_request.save()
    messages.warning(request, 'Request rejected.')
    return redirect('request_list')
