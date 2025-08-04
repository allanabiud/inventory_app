from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.timezone import now

from .models import StockAlert


@shared_task
def send_low_stock_summary_email():
    alerts = StockAlert.objects.filter(alert_type="low_stock", is_resolved=False)

    if not alerts.exists():
        return

    subject = "[Stockflow] Daily Low Stock Summary"
    from_email = settings.DEFAULT_FROM_EMAIL
    to = [settings.EMAIL_HOST_USER]

    context = {
        "alerts": alerts,
        "date": now(),
    }

    html_content = render_to_string("emails/low_stock_summary.html", context)
    text_content = "Low stock alerts:\n\n" + "\n".join(
        [f"{a.item.name}: {a.message}" for a in alerts]
    )

    msg = EmailMultiAlternatives(subject, text_content, from_email, to)
    msg.attach_alternative(html_content, "text/html")
    msg.send()
