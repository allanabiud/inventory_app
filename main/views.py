from django.contrib.auth.decorators import login_required
from django.db import models
from django.shortcuts import render

from inventory.models import Category, Item


@login_required
def home(request):
    items = Item.objects.all()
    categories = Category.objects.all()
    num_items = items.count()
    num_categories = categories.count()

    low_stock_count = items.filter(current_stock__lte=models.F("reorder_point")).count()
    sufficient_stock_count = num_items - low_stock_count

    context = {
        "items": items,
        "num_items": num_items,
        "num_categories": num_categories,
        "low_stock_count": low_stock_count,
        "sufficient_stock_count": sufficient_stock_count,
    }
    return render(request, "home.html", context)
