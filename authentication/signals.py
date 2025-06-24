from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import InvitedUser
from .utils import send_invitation_email


@receiver(post_save, sender=InvitedUser)
def send_invite_on_create(sender, instance, created, **kwargs):
    if created:
        send_invitation_email(instance)
