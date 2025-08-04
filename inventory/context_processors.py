from .models import StockAlert


def low_stock_alerts(request):
    low_stock = StockAlert.objects.filter(is_resolved=False).count()
    print(low_stock)
    return {"low_stock": low_stock}
