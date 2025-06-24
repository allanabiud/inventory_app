from django.contrib.auth.models import User
from django.db import models


class InvitedUser(models.Model):
    email = models.EmailField(unique=True)
    invited_at = models.DateTimeField(auto_now_add=True)
    accepted = models.BooleanField(default=False)
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.email
