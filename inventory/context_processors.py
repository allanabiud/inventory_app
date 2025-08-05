from django.db import models

from .models import Item


def low_stock_alerts(request):
    low_stock = Item.objects.filter(
        current_stock__lte=models.F("reorder_point")
    ).count()
    return {"low_stock": low_stock}
