import os
import uuid
from datetime import datetime

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.urls import reverse
from itsdangerous import URLSafeTimedSerializer


def send_invitation_email(invited_user):
    s = URLSafeTimedSerializer(settings.SECRET_KEY)
    token = s.dumps(invited_user.email, salt="invitation")

    signup_path = reverse("signup", kwargs={"token": token})
    signup_url = f"{settings.SITE_DOMAIN}{signup_path}"

    subject = "You're Invited to Join Stockflow"
    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = [invited_user.email]

    html_content = render_to_string(
        "emails/invitation_email.html",
        {
            "signup_url": signup_url,
            "user": invited_user,
        },
    )

    msg = EmailMultiAlternatives(subject, "", from_email, to_email)
    msg.attach_alternative(html_content, "text/html")
    msg.send()


def user_image_upload_path(instance, filename):
    ext = filename.split(".")[-1]
    username = instance.user.username.replace(" ", "_").lower()
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    unique_id = uuid.uuid4().hex[:6]
    filename = f"{username}_{timestamp}_{unique_id}.{ext}"
    return os.path.join("profile_images", username, filename)
