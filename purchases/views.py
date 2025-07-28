from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from purchases.models import Purchase

from .forms import PurchaseForm
from .utils import generate_purchase_number


@login_required
def purchases_view(request):
    purchases = Purchase.objects.select_related("item").order_by("-created_at")
    total_purchases = purchases.count()

    return render(
        request,
        "purchases.html",
        {
            "purchases": purchases,
            "total_purchases": total_purchases,
        },
    )


@login_required
def add_purchase(request):
    if request.method == "POST":
        form = PurchaseForm(request.POST)
        if form.is_valid():
            purchase = form.save(commit=False)
            purchase.user = request.user
            # Generate purchase number *after* counting existing purchases
            purchase_number = generate_purchase_number()
            purchase.purchase_number = (
                purchase_number  # assuming you have a purchase_number field
            )
            purchase.save()
            messages.success(
                request, f"Purchase recorded successfully for {purchase.item.name}."
            )
            return redirect("purchases")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = PurchaseForm()
        purchase_number_preview = generate_purchase_number()

    return render(
        request,
        "forms/add/add_purchase.html",
        {
            "form": form,
            "purchase_number": purchase_number_preview if request.method != "POST" else None,  # type: ignore
        },
    )


@login_required
def edit_purchase(request, pk):
    purchase = get_object_or_404(Purchase, id=pk)
    old_item = purchase.item
    old_quantity = purchase.quantity

    if request.method == "POST":
        form = PurchaseForm(request.POST, instance=purchase)
        if form.is_valid():
            updated_purchase = form.save(commit=False)

            if updated_purchase.item != old_item:
                # Remove quantity from old item
                if old_item:
                    old_item.current_stock -= old_quantity
                    old_item.save()
                # Add quantity to new item
                if updated_purchase.item:
                    updated_purchase.item.current_stock += updated_purchase.quantity
                    updated_purchase.item.save()
            else:
                # Same item, adjust stock difference
                quantity_diff = updated_purchase.quantity - old_quantity
                updated_purchase.item.current_stock += quantity_diff
                updated_purchase.item.save()

            updated_purchase.save()
            messages.success(request, "Purchase updated successfully.")
            return redirect("view_purchase", pk=updated_purchase.pk)
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = PurchaseForm(instance=purchase)

    return render(
        request,
        "forms/edit/edit_purchase.html",
        {
            "form": form,
            "purchase": purchase,
        },
    )


@login_required
def view_purchase(request, pk):
    purchase = get_object_or_404(Purchase, pk=pk)
    return render(
        request,
        "view/view_purchase.html",
        {"purchase": purchase},
    )


@login_required
def delete_purchase(request, pk):
    purchase = get_object_or_404(Purchase, pk=pk)
    if request.method == "POST":
        purchase.delete()
        messages.success(
            request, f'Purchase record for "{purchase.item.name}" deleted.'
        )
        return redirect("purchases")
    return redirect("view_purchase", pk=pk)


@login_required
def delete_all_purchases(request):
    if request.method == "POST":
        for purchase in Purchase.objects.all():
            purchase.delete()  # Triggers signal
        messages.success(request, "All purchases deleted and stock levels updated.")
    return redirect("purchases")
