from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from inventory.models import Category, Item


@login_required
def home(request):
    items = Item.objects.all()
    categories = Category.objects.all()
    num_items = items.count()
    num_categories = categories.count()
    context = {
        "items": items,
        "num_items": num_items,
        "num_categories": num_categories,
    }
    return render(request, "home.html", context)
