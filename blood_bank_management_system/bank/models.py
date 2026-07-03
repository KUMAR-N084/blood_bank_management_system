from django.db import models

BLOOD_GROUPS = [
    ('A+', 'A+'), ('A-', 'A-'),
    ('B+', 'B+'), ('B-', 'B-'),
    ('AB+', 'AB+'), ('AB-', 'AB-'),
    ('O+', 'O+'), ('O-', 'O-'),
]

GENDER_CHOICES = [
    ('Male', 'Male'),
    ('Female', 'Female'),
    ('Other', 'Other'),
]

STATUS_CHOICES = [
    ('Pending', 'Pending'),
    ('Approved', 'Approved'),
    ('Rejected', 'Rejected'),
]

class Donor(models.Model):
    name = models.CharField(max_length=100)
    age = models.PositiveIntegerField()
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    phone = models.CharField(max_length=15)
    email = models.EmailField(blank=True)
    address = models.TextField()
    city = models.CharField(max_length=100, blank=True)
    blood_group = models.CharField(max_length=5, choices=BLOOD_GROUPS)
    last_donation_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.blood_group}"

class BloodStock(models.Model):
    blood_group = models.CharField(max_length=5, choices=BLOOD_GROUPS, unique=True)
    units = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.blood_group}: {self.units} units"

class BloodRequest(models.Model):
    patient_name = models.CharField(max_length=100)
    hospital_name = models.CharField(max_length=120)
    contact_number = models.CharField(max_length=15)
    blood_group = models.CharField(max_length=5, choices=BLOOD_GROUPS)
    units_required = models.PositiveIntegerField()
    reason = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    request_date = models.DateTimeField(auto_now_add=True)
    notification = models.TextField(blank=True, default='')
    contact_email = models.EmailField(blank=True, default='')

    def __str__(self):
        return f"{self.patient_name} - {self.blood_group}"


class DonorApplication(models.Model):
    name = models.CharField(max_length=100)
    age = models.PositiveIntegerField()
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    phone = models.CharField(max_length=15)
    email = models.EmailField(blank=True)
    address = models.TextField()
    city = models.CharField(max_length=100, blank=True)
    blood_group = models.CharField(max_length=5, choices=BLOOD_GROUPS)
    last_donation_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    applied_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Application: {self.name} - {self.blood_group} ({self.status})"


class DonationAppointment(models.Model):
    APPT_STATUS = [
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ]
    donor = models.ForeignKey(Donor, null=True, blank=True, on_delete=models.SET_NULL)
    donor_name = models.CharField(max_length=100)
    donor_email = models.EmailField(blank=True)
    donor_phone = models.CharField(max_length=15, blank=True)
    hospital = models.CharField(max_length=120, blank=True)
    slot = models.DateTimeField()
    status = models.CharField(max_length=20, choices=APPT_STATUS, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Appointment: {self.donor_name} @ {self.slot} - {self.status}"


class ContactRequest(models.Model):
    STATUS = [('Pending','Pending'),('Approved','Approved'),('Rejected','Rejected')]
    donor = models.ForeignKey(Donor, on_delete=models.CASCADE)
    requester_name = models.CharField(max_length=100)
    requester_contact = models.CharField(max_length=120)
    message = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"ContactRequest: {self.requester_name} -> {self.donor.name} ({self.status})"


class AuditLog(models.Model):
    actor = models.ForeignKey('auth.User', null=True, on_delete=models.SET_NULL)
    action = models.CharField(max_length=200)
    target = models.CharField(max_length=200, blank=True)
    details = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.timestamp} - {self.actor} - {self.action}"
