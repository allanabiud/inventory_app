from django.contrib.auth.models import User
from django.db import models

from .utils import user_image_upload_path


class InvitedUser(models.Model):
    email = models.EmailField(unique=True)
    invited_at = models.DateTimeField(auto_now_add=True)
    accepted = models.BooleanField(default=False)
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.email


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_image = models.ImageField(upload_to=user_image_upload_path, null=True)

    def __str__(self):
        return self.user.username
