from django.contrib import admin
from .models import (
    Donor, BloodStock, BloodRequest,
    DonorApplication, DonationAppointment,
    ContactRequest, AuditLog,
)


@admin.register(Donor)
class DonorAdmin(admin.ModelAdmin):
    list_display = ('name', 'blood_group', 'age', 'gender', 'phone', 'city', 'created_at')
    search_fields = ('name', 'phone', 'blood_group', 'city')
    list_filter = ('blood_group', 'gender', 'city')


@admin.register(BloodStock)
class BloodStockAdmin(admin.ModelAdmin):
    list_display = ('blood_group', 'units', 'updated_at')
    list_filter = ('blood_group',)


@admin.register(BloodRequest)
class BloodRequestAdmin(admin.ModelAdmin):
    list_display = ('patient_name', 'hospital_name', 'blood_group', 'units_required', 'status', 'request_date')
    search_fields = ('patient_name', 'hospital_name', 'contact_number')
    list_filter = ('blood_group', 'status')


@admin.register(DonorApplication)
class DonorApplicationAdmin(admin.ModelAdmin):
    list_display = ('name', 'blood_group', 'age', 'gender', 'phone', 'status', 'applied_at')
    search_fields = ('name', 'phone', 'blood_group')
    list_filter = ('blood_group', 'status', 'gender')


@admin.register(DonationAppointment)
class DonationAppointmentAdmin(admin.ModelAdmin):
    list_display = ('donor_name', 'hospital', 'slot', 'status', 'created_at')
    search_fields = ('donor_name', 'hospital')
    list_filter = ('status',)


@admin.register(ContactRequest)
class ContactRequestAdmin(admin.ModelAdmin):
    list_display = ('donor', 'requester_name', 'requester_contact', 'status', 'created_at')
    search_fields = ('requester_name', 'donor__name')
    list_filter = ('status',)


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'actor', 'action', 'target')
    search_fields = ('action', 'target', 'actor__username')
    list_filter = ('actor',)
    readonly_fields = ('timestamp', 'actor', 'action', 'target', 'details')
