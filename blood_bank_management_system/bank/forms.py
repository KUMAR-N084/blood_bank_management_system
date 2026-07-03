from django import forms
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from django.utils import timezone
from .models import Donor, BloodStock, BloodRequest

phone_validator = RegexValidator(r'^[0-9()+ -]{7,15}$', 'Enter a valid phone number (7-15 digits, may include + - parentheses).')
name_validator = RegexValidator(r'^[A-Za-z .\'-]+$', 'Enter a valid name (letters, spaces, dot, apostrophe, hyphen).')

class DonorForm(forms.ModelForm):
    name = forms.CharField(max_length=100, validators=[name_validator])
    age = forms.IntegerField(validators=[MinValueValidator(18), MaxValueValidator(100)])
    phone = forms.CharField(validators=[phone_validator], max_length=15)

    class Meta:
        model = Donor
        fields = ['name', 'age', 'gender', 'phone', 'email', 'address', 'city', 'blood_group', 'last_donation_date']
        widgets = {
            'last_donation_date': forms.DateInput(attrs={'type': 'date'}),
            'address': forms.Textarea(attrs={'rows': 3}),
        }

    def clean_name(self):
        return self.cleaned_data['name'].strip()


class BloodStockForm(forms.ModelForm):
    class Meta:
        model = BloodStock
        fields = ['blood_group', 'units']


class BloodRequestForm(forms.ModelForm):
    patient_name = forms.CharField(max_length=100, validators=[name_validator])
    contact_number = forms.CharField(validators=[phone_validator], max_length=15)

    class Meta:
        model = BloodRequest
        fields = ['patient_name', 'hospital_name', 'contact_number', 'contact_email', 'blood_group', 'units_required', 'reason']
        widgets = {
            'reason': forms.Textarea(attrs={'rows': 3}),
        }


from .models import DonorApplication, ContactRequest
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class UserRegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')


class DonorApplicationForm(forms.ModelForm):
    name = forms.CharField(max_length=100, validators=[name_validator])
    age = forms.IntegerField(validators=[MinValueValidator(18), MaxValueValidator(100)])
    phone = forms.CharField(validators=[phone_validator], max_length=15)

    class Meta:
        model = DonorApplication
        fields = ['name', 'age', 'gender', 'phone', 'email', 'address', 'city', 'blood_group', 'last_donation_date']


class DonationAppointmentForm(forms.Form):
    donor_name = forms.CharField(max_length=100, validators=[name_validator])
    donor_email = forms.EmailField(required=False)
    donor_phone = forms.CharField(max_length=15, required=False, validators=[phone_validator])
    hospital = forms.CharField(max_length=120, required=False)
    slot = forms.DateTimeField(widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}))

    def clean_slot(self):
        slot = self.cleaned_data.get('slot')
        if slot and slot <= timezone.now():
            raise forms.ValidationError('Please choose a future date and time for the appointment.')
        return slot


def validate_contact_info(value):
    from django.core.validators import validate_email
    from django.core.exceptions import ValidationError
    try:
        validate_email(value)
        return
    except ValidationError:
        pass
    try:
        phone_validator(value)
    except ValidationError:
        raise ValidationError('Enter a valid email address or phone number.')


class ContactRequestForm(forms.ModelForm):
    requester_name = forms.CharField(max_length=100, validators=[name_validator])
    requester_contact = forms.CharField(max_length=120, validators=[validate_contact_info])

    class Meta:
        model = ContactRequest
        fields = ['donor', 'requester_name', 'requester_contact', 'message']

