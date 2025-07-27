from django.contrib.auth.decorators import login_required
from django.db import models
from django.db.models import ExpressionWrapper, F, FloatField, Q, Sum
from django.shortcuts import render
from django.utils import timezone

from inventory.models import Category, Item
from sales.models import Sale

# from inventory.models import Customer, Vendor # Uncomment when these models are implemented


@login_required
def home(request):
    items = Item.objects.all()
    categories = Category.objects.all()
    num_items = items.count()
    num_categories = categories.count()

    low_stock_count = items.filter(current_stock__lte=models.F("reorder_point")).count()
    sufficient_stock_count = num_items - low_stock_count

    # Top 10 selling items
    top_selling_items = (
        Sale.objects.values("item__name", "item__unit__name")
        .annotate(
            total_quantity=Sum("quantity"),
            total_sales=Sum(
                ExpressionWrapper(
                    F("quantity") * F("unit_price"), output_field=FloatField()
                )
            ),
        )
        .order_by("-total_quantity")[:10]
    )

    recent_sales = Sale.objects.select_related("item", "item__unit").order_by("-date")[
        :10
    ]

    context = {
        "items": items,
        "num_items": num_items,
        "num_categories": num_categories,
        "low_stock_count": low_stock_count,
        "sufficient_stock_count": sufficient_stock_count,
        "top_selling_items": top_selling_items,
        "recent_sales": recent_sales,
        "now": timezone.now(),
    }
    return render(request, "home.html", context)


@login_required
def search_results_view(request):
    query = request.GET.get("q", "").strip()
    scope = request.GET.get("scope", "all")  # Default scope to 'all'

    # Initialize results containers
    item_results = None
    category_results = None
    customer_results = None  # None until implemented
    vendor_results = None  # None until implemented

    if query:
        # Search in Items
        if scope == "items" or scope == "all":
            item_results = Item.objects.filter(
                Q(name__icontains=query) | Q(sku__icontains=query)
            ).distinct()

        # Search in Categories
        if scope == "categories" or scope == "all":
            category_results = Category.objects.filter(name__icontains=query).distinct()

        # if scope == 'customers' or scope == 'all':
        #     customer_results = Customer.objects.filter(
        #         Q(name__icontains=query) |
        #         Q(email__icontains=query) |
        #         Q(phone_number__icontains=query)
        #     ).distinct()

        # if scope == 'vendors' or scope == 'all':
        #     vendor_results = Vendor.objects.filter(
        #         Q(name__icontains=query) |
        #         Q(contact_person__icontains=query) |
        #         Q(email__icontains=query) |
        #         Q(phone_number__icontains=query)
        #     ).distinct()

    context = {
        "query": query,
        "scope": scope,  # Pass back to the template to restore state
        "item_results": item_results,
        "category_results": category_results,
        "customer_results": customer_results,
        "vendor_results": vendor_results,
    }
    return render(request, "search/search_results.html", context)


# views.py
def custom_404_view(request, exception):
    return render(request, "errors/404.html")


def custom_500_view(request):
    return render(request, "errors/500.html")
