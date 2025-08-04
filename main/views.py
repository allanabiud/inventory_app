import json
from datetime import timedelta

from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.db import models
from django.db.models import (
    CharField,
    DecimalField,
    ExpressionWrapper,
    F,
    FloatField,
    Q,
    Sum,
    Value,
)
from django.db.models.functions import TruncDay, TruncMonth
from django.shortcuts import render
from django.utils import timezone
from django_celery_beat.models import PeriodicTask

from authentication.models import InvitedUser
from inventory.models import Category, Item
from purchases.models import Purchase
from sales.models import Sale


@login_required
def home(request):
    items = Item.objects.all()
    categories = Category.objects.all()
    num_items = items.count()
    num_categories = categories.count()

    low_stock_count = items.filter(current_stock__lte=models.F("reorder_point")).count()
    sufficient_stock_count = num_items - low_stock_count

    sales_summary = Sale.objects.aggregate(
        total_quantity_sold=Sum("quantity"),
        total_sales_value=Sum(
            ExpressionWrapper(
                F("quantity") * F("unit_price"), output_field=FloatField()
            )
        ),
    )

    purchase_summary = Purchase.objects.aggregate(
        total_quantity_purchased=Sum("quantity"),
        total_purchase_cost=Sum(
            ExpressionWrapper(
                F("quantity") * F("unit_cost"),
                output_field=DecimalField(max_digits=10, decimal_places=2),
            )
        ),
    )

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

    recent_sales = (
        Sale.objects.select_related("item", "item__unit")
        .annotate(
            transaction_type=Value("sale", output_field=CharField()),
            total_amount=ExpressionWrapper(
                F("quantity") * F("unit_price"), output_field=FloatField()
            ),
        )
        .values(
            "date",
            "item__name",
            "quantity",
            "item__unit__name",
            "total_amount",
            "transaction_type",
            "created_at",
        )
    )

    recent_purchases = (
        Purchase.objects.select_related("item", "item__unit")
        .annotate(
            transaction_type=Value("purchase", output_field=CharField()),
            total_amount=ExpressionWrapper(
                F("quantity") * F("unit_cost"), output_field=FloatField()
            ),
        )
        .values(
            "date",
            "item__name",
            "quantity",
            "item__unit__name",
            "total_amount",
            "transaction_type",
            "created_at",
        )
    )

    all_recent_transactions = recent_sales.union(recent_purchases).order_by(
        "-date", "-created_at"
    )[:5]

    today = timezone.now().date()
    current_year = today.year
    start_of_month = today.replace(day=1)
    start_of_year = today.replace(month=1, day=1)

    raw_monthly_sales = (
        Sale.objects.filter(date__gte=start_of_month)
        .annotate(day=TruncDay("date"))
        .values("day")
        .annotate(total=Sum(F("quantity") * F("unit_price")))
    )
    sales_lookup = {entry["day"]: float(entry["total"]) for entry in raw_monthly_sales}

    raw_monthly_purchases = (
        Purchase.objects.filter(date__gte=start_of_month)
        .annotate(day=TruncDay("date"))
        .values("day")
        .annotate(total=Sum(F("quantity") * F("unit_cost")))
    )
    purchase_lookup = {
        entry["day"]: float(entry["total"]) for entry in raw_monthly_purchases
    }

    days_in_month = []
    current = start_of_month
    while current.month == start_of_month.month:
        days_in_month.append(current)
        current += timedelta(days=1)

    monthly_sales_filled = [
        {"day": day, "total": sales_lookup.get(day, 0.0)} for day in days_in_month
    ]

    monthly_purchases_filled = [
        {"day": day, "total": purchase_lookup.get(day, 0.0)} for day in days_in_month
    ]

    # --- Yearly Chart Data (NEW) ---
    raw_yearly_sales = (
        Sale.objects.filter(date__year=current_year)
        .annotate(month=TruncMonth("date"))
        .values("month")
        .annotate(total=Sum(F("quantity") * F("unit_price")))
    )
    sales_lookup_year = {
        entry["month"]: float(entry["total"]) for entry in raw_yearly_sales
    }

    raw_yearly_purchases = (
        Purchase.objects.filter(date__year=current_year)
        .annotate(month=TruncMonth("date"))
        .values("month")
        .annotate(total=Sum(F("quantity") * F("unit_cost")))
    )
    purchase_lookup_year = {
        entry["month"]: float(entry["total"]) for entry in raw_yearly_purchases
    }

    months_in_year = []
    current_month = start_of_year
    while current_month.year == current_year:
        months_in_year.append(current_month)
        current_month = (current_month.replace(day=1) + timedelta(days=32)).replace(
            day=1
        )  # Move to next month safely

    yearly_sales_filled = [
        {"month": month, "total": sales_lookup_year.get(month, 0.0)}
        for month in months_in_year
    ]

    yearly_purchases_filled = [
        {"month": month, "total": purchase_lookup_year.get(month, 0.0)}
        for month in months_in_year
    ]

    def serialize_chart_data(sales_data, purchases_data, label_field):
        labels = []
        raw_dates = []
        if label_field == "day":
            labels = [str(entry[label_field].day) for entry in sales_data]
            raw_dates = [
                entry[label_field].strftime("%Y-%m-%d") for entry in sales_data
            ]
        elif label_field == "month":
            labels = [
                entry[label_field].strftime("%b") for entry in sales_data
            ]  # e.g., Jan, Feb
            raw_dates = [
                entry[label_field].strftime("%Y-%m-%d") for entry in sales_data
            ]  # Still useful for tooltips

        sales_dataset = {
            "label": "Sales",
            "data": [round(float(entry["total"]), 2) for entry in sales_data],
        }

        purchases_dataset = {
            "label": "Purchases",
            "data": [round(float(entry["total"]), 2) for entry in purchases_data],
        }

        return {
            "labels": labels,
            "rawDates": raw_dates,
            "datasets": [sales_dataset, purchases_dataset],
        }

    # Determine current filter for context
    active_filter = request.GET.get("time_filter", "month")  # Default to 'month'

    context = {
        "items": items,
        "num_items": num_items,
        "num_categories": num_categories,
        "low_stock_count": low_stock_count,
        "sufficient_stock_count": sufficient_stock_count,
        "top_selling_items": top_selling_items,
        "recent_transactions": all_recent_transactions,
        "now": timezone.now(),
        "total_quantity_sold": sales_summary["total_quantity_sold"] or 0,
        "total_sales_value": sales_summary["total_sales_value"] or 0.00,
        "total_quantity_purchased": purchase_summary["total_quantity_purchased"] or 0,
        "total_purchase_cost": purchase_summary["total_purchase_cost"] or 0.00,
        "monthly_chart_data": json.dumps(
            serialize_chart_data(monthly_sales_filled, monthly_purchases_filled, "day")
        ),
        "yearly_chart_data": json.dumps(
            serialize_chart_data(yearly_sales_filled, yearly_purchases_filled, "month")
        ),
        "active_filter": active_filter,
    }

    return render(request, "home.html", context)


@login_required
def search_results_view(request):
    query = request.GET.get("q", "").strip()
    scope = request.GET.get("scope", "all")  # Default scope to 'all'

    # Initialize results containers
    item_results = None
    category_results = None

    if query:
        # Search in Items
        if scope == "items" or scope == "all":
            item_results = Item.objects.filter(
                Q(name__icontains=query) | Q(sku__icontains=query)
            ).distinct()

        # Search in Categories
        if scope == "categories" or scope == "all":
            category_results = Category.objects.filter(name__icontains=query).distinct()

    context = {
        "query": query,
        "scope": scope,  # Pass back to the template to restore state
        "item_results": item_results,
        "category_results": category_results,
    }
    return render(request, "search/search_results.html", context)


def custom_404_view(request, exception):
    return render(request, "errors/404.html")


def custom_500_view(request):
    return render(request, "errors/500.html")


@user_passes_test(lambda u: u.is_superuser)  # type: ignore
@login_required
def settings_view(request):
    tasks = PeriodicTask.objects.exclude(task="celery.backend_cleanup")
    users = User.objects.all().select_related("inviteduser")
    pending_invites = InvitedUser.objects.filter(accepted=False, user__isnull=True)
    context = {"tasks": tasks, "users": users, "pending_invites": pending_invites}
    return render(request, "settings/settings.html", context)
