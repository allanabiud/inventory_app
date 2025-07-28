import json
from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.db import models
from django.db.models import ExpressionWrapper, F, FloatField, Q, Sum
from django.db.models.functions import TruncDay, TruncMonth
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

    # Top 5 selling items
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
        .order_by("-total_quantity")[:5]
    )

    # 5 Recent Sales
    recent_sales = Sale.objects.select_related("item", "item__unit").order_by("-date")[
        :5
    ]

    sales_summary = Sale.objects.aggregate(
        total_quantity_sold=Sum("quantity"),
        total_sales_value=Sum(
            ExpressionWrapper(
                F("quantity") * F("unit_price"), output_field=FloatField()
            )
        ),
    )

    # CHART DATA
    today = timezone.now().date()
    start_of_month = today.replace(day=1)
    start_of_year = today.replace(month=1, day=1)

    # Raw sales data grouped by day
    raw_monthly_sales = (
        Sale.objects.filter(date__gte=start_of_month)
        .annotate(day=TruncDay("date"))
        .values("day")
        .annotate(total=Sum(F("quantity") * F("unit_price")))
    )
    # Build a lookup: {date: total}
    sales_lookup = {entry["day"]: float(entry["total"]) for entry in raw_monthly_sales}

    # Generate all days of the month
    days_in_month = []
    current = start_of_month
    while current.month == start_of_month.month:
        days_in_month.append(current)
        current += timedelta(days=1)

    # Fill in data with zero where missing
    monthly_sales_filled = [
        {"day": day, "total": sales_lookup.get(day, 0.0)} for day in days_in_month
    ]

    # Yearly Sales: group by month
    yearly_sales = (
        Sale.objects.filter(date__gte=start_of_year)
        .annotate(month=TruncMonth("date"))
        .values("month")
        .annotate(total=Sum(F("quantity") * F("unit_price")))
        .order_by("month")
    )

    def serialize_chart_data(queryset, label_field):
        return {
            "labels": [
                (
                    str(entry[label_field].day)
                    if label_field == "day"
                    else entry[label_field].strftime("%b")
                )
                for entry in queryset
            ],
            "rawDates": [entry[label_field].strftime("%Y-%m-%d") for entry in queryset],
            "datasets": [
                {
                    "label": "Sales",
                    "data": [round(float(entry["total"]), 2) for entry in queryset],
                }
            ],
        }

    # Define context first
    context = {
        "items": items,
        "num_items": num_items,
        "num_categories": num_categories,
        "low_stock_count": low_stock_count,
        "sufficient_stock_count": sufficient_stock_count,
        "top_selling_items": top_selling_items,
        "recent_sales": recent_sales,
        "now": timezone.now(),
        "total_quantity_sold": sales_summary["total_quantity_sold"] or 0,
        "total_sales_value": sales_summary["total_sales_value"] or 0.00,
        "monthly_chart": json.dumps(serialize_chart_data(monthly_sales_filled, "day")),
        "yearly_chart": json.dumps(serialize_chart_data(yearly_sales, "month")),
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
