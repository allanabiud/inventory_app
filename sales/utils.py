from django.utils.timezone import now

from .models import Sale


def generate_sales_number():
    """
    Ensures the generated sales number is unique by checking the DB.
    """
    today = now().date()
    date_str = today.strftime("%Y%m%d")
    suffix = Sale.objects.filter(date=today).count() + 1

    while True:
        number = f"SALE-{date_str}-{suffix:03d}"
        if not Sale.objects.filter(sales_number=number).exists():
            return number
        suffix += 1
