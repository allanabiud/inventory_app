from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.core.management.base import BaseCommand
from django.template.loader import render_to_string
from django.utils import timezone

from inventory.models import StockAlert


class Command(BaseCommand):
    help = "Send daily low stock summary email"

    def handle(self, *args, **kwargs):
        alerts = StockAlert.objects.filter(
            alert_type="low_stock", is_resolved=False, notified_by_email=False
        ).select_related("item")

        if not alerts.exists():
            self.stdout.write("No new low stock alerts to email.")
            return

        context = {"alerts": alerts, "date": timezone.now()}

        subject = "[Stockflow] Daily Low Stock Summary"
        from_email = settings.DEFAULT_FROM_EMAIL
        to = [settings.EMAIL_HOST_USER]  # Or customize recipients

        html_content = render_to_string("emails/low_stock_summary.html", context)
        text_content = "\n\n".join([alert.message for alert in alerts])

        msg = EmailMultiAlternatives(subject, text_content, from_email, to)
        msg.attach_alternative(html_content, "text/html")

        try:
            msg.send()
            alerts.update(notified_by_email=True)
            self.stdout.write(self.style.SUCCESS("Low stock email sent."))
        except Exception as e:
            self.stderr.write(f"Error sending email: {e}")
