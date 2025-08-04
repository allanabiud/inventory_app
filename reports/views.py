from django.contrib.auth.decorators import login_required
from django.db.models import DecimalField, ExpressionWrapper, F, Sum
from django.shortcuts import render

from purchases.models import Purchase
from sales.models import Sale


@login_required
def sales_report_view(request):
    sales = Sale.objects.select_related("item", "customer", "user").order_by("-date")

    # Optional: filter by date range
    start_date = request.GET.get("start")
    end_date = request.GET.get("end")
    if start_date and end_date:
        sales = sales.filter(date__range=[start_date, end_date])

    # Annotate for display
    sales = sales.annotate(
        total=ExpressionWrapper(
            F("unit_price") * F("quantity"),
            output_field=DecimalField(max_digits=10, decimal_places=2),
        ),
        expected_total=ExpressionWrapper(
            F("item__selling_price") * F("quantity"),
            output_field=DecimalField(max_digits=10, decimal_places=2),
        ),
        discount_amount=ExpressionWrapper(
            F("item__selling_price") * F("quantity") - F("unit_price") * F("quantity"),
            output_field=DecimalField(max_digits=10, decimal_places=2),
        ),
    )

    # Use raw expressions in aggregation
    total_sales = (
        sales.aggregate(
            total=Sum(
                ExpressionWrapper(
                    F("unit_price") * F("quantity"),
                    output_field=DecimalField(max_digits=10, decimal_places=2),
                )
            )
        )["total"]
        or 0
    )

    total_discount = (
        sales.aggregate(
            total=Sum(
                ExpressionWrapper(
                    F("item__selling_price") * F("quantity")
                    - F("unit_price") * F("quantity"),
                    output_field=DecimalField(max_digits=10, decimal_places=2),
                )
            )
        )["total"]
        or 0
    )

    total_quantity = sales.aggregate(total=Sum("quantity"))["total"] or 0

    return render(
        request,
        "sales_report.html",
        {
            "sales": sales,
            "total_sales": total_sales,
            "total_discount": total_discount,
            "total_quantity": total_quantity,
            "start_date": start_date,
            "end_date": end_date,
        },
    )


@login_required
def purchases_report_view(request):
    purchases = Purchase.objects.select_related("item", "supplier", "user").order_by(
        "-date"
    )

    # Optional: filter by date range
    start_date = request.GET.get("start")
    end_date = request.GET.get("end")
    if start_date and end_date:
        purchases = purchases.filter(date__range=[start_date, end_date])

    # Annotate with total cost
    purchases = purchases.annotate(
        total=ExpressionWrapper(
            F("unit_cost") * F("quantity"),
            output_field=DecimalField(max_digits=10, decimal_places=2),
        )
    )

    # Aggregated totals
    total_purchases = (
        purchases.aggregate(
            total=Sum(
                ExpressionWrapper(
                    F("unit_cost") * F("quantity"),
                    output_field=DecimalField(max_digits=10, decimal_places=2),
                )
            )
        )["total"]
        or 0
    )

    total_quantity = purchases.aggregate(total=Sum("quantity"))["total"] or 0

    return render(
        request,
        "purchases_report.html",  # use your actual template name
        {
            "purchases": purchases,
            "total_purchases": total_purchases,
            "total_quantity": total_quantity,
            "start_date": start_date,
            "end_date": end_date,
        },
    )


@login_required
def profit_loss_report_view(request):
    start_date = request.GET.get("start")
    end_date = request.GET.get("end")

    sales_qs = Sale.objects.select_related("item")
    if start_date and end_date:
        sales_qs = sales_qs.filter(date__range=[start_date, end_date])

    profit_data = []
    total_sales = 0
    total_cost = 0
    total_profit = 0

    for sale in sales_qs:
        item = sale.item
        unit_cost = item.purchase_price
        total_sale = sale.unit_price * sale.quantity
        total_c = unit_cost * sale.quantity
        profit = total_sale - total_c

        profit_data.append(
            {
                "date": sale.date,
                "item": item,
                "quantity": sale.quantity,
                "unit_price": sale.unit_price,
                "total_sales": total_sale,
                "unit_cost": unit_cost,
                "total_cost": total_c,
                "profit": profit,
            }
        )

        total_sales += total_sale
        total_cost += total_c
        total_profit += profit

    context = {
        "profit_data": profit_data,
        "total_sales": total_sales,
        "total_cost": total_cost,
        "total_profit": total_profit,
        "start_date": start_date,
        "end_date": end_date,
    }

    return render(request, "profit_loss_report.html", context)
