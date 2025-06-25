from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .models import Item


@login_required
def items_view(request):
    items = Item.objects.all()
    context = {"items": items}
    return render(request, "items.html", context)
