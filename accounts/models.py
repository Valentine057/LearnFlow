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
