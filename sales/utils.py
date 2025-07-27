from django.utils.timezone import now

from .models import Sale


def generate_sales_number():
    """
    Generates a unique sales number in the format SALE-YYYYMMDD-XXX
    """
    today = now().date()
    date_str = today.strftime("%Y%m%d")
    sales_count = Sale.objects.filter(date=today).count() + 1
    return f"SALE-{date_str}-{sales_count:03d}"
