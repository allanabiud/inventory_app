from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.db import models
from django.template.loader import render_to_string
from django.utils.timezone import now

from .models import Item


@shared_task
def send_low_stock_summary_email():
    low_stock_items = Item.objects.filter(current_stock__lt=models.F("reorder_point"))

    if not low_stock_items.exists():
        return  # Nothing to send

    subject = "[Stockflow] Daily Low Stock Summary"
    from_email = settings.DEFAULT_FROM_EMAIL
    to = [settings.EMAIL_HOST_USER]

    context = {
        "items": low_stock_items,
        "date": now(),
    }

    html_content = render_to_string("emails/low_stock_summary.html", context)
    text_content = "Low stock items:\n\n" + "\n".join(
        [
            f"{item.name} (SKU: {item.sku}) — Stock: {item.current_stock}, Reorder point: {item.reorder_point}"
            for item in low_stock_items
        ]
    )

    msg = EmailMultiAlternatives(subject, text_content, from_email, to)
    msg.attach_alternative(html_content, "text/html")
    msg.send()
