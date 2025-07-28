from django.utils.timezone import now

from .models import Purchase


def generate_purchase_number():
    """
    Ensures the generated purchase number is unique by checking the DB.
    """
    today = now().date()
    date_str = today.strftime("%Y%m%d")
    suffix = Purchase.objects.filter(date=today).count() + 1

    while True:
        number = f"PUR-{date_str}-{suffix:03d}"
        if not Purchase.objects.filter(purchase_number=number).exists():
            return number
        suffix += 1
