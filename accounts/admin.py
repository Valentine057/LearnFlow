from django.contrib import admin
from .models import InstructorProfile, SchoolOwnerProfile


@admin.register(InstructorProfile)
class InstructorProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'expertise', 'is_verified')
    search_fields = ('user__username', 'user__email', 'expertise')
    list_filter = ('is_verified',)


@admin.register(SchoolOwnerProfile)
class SchoolOwnerProfileAdmin(admin.ModelAdmin):
    list_display = ('school_name', 'user', 'contact_email', 'phone_number')
    search_fields = ('school_name', 'user__username', 'contact_email')
