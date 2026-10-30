from django.conf import settings
from django.db import models


class InstructorProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='instructor_profile')
    bio = models.TextField(blank=True)
    expertise = models.CharField(max_length=180, blank=True)
    photo = models.FileField(upload_to='instructors/', blank=True, null=True)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.user.get_full_name() or self.user.username


class SchoolOwnerProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='school_owner_profile',
    )
    school_name = models.CharField(max_length=180)
    contact_email = models.EmailField(blank=True)
    phone_number = models.CharField(max_length=40, blank=True)

    def __str__(self):
        return f'{self.school_name} ({self.user.get_username()})'
