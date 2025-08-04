from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from authentication.models import UserProfile
from inventory.utils import check_and_create_low_stock_alert
from purchases.models import Purchase, Supplier

from .forms import PurchaseForm, SupplierForm
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
            # Check and create low stock alert if necessary
            check_and_create_low_stock_alert(purchase.item)

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
    user_profile = (
        UserProfile.objects.filter(user=purchase.user).first()
        if purchase.user
        else None
    )
    context = {
        "purchase": purchase,
        "user_profile": user_profile,
    }
    return render(
        request,
        "view/view_purchase.html",
        context,
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


@login_required
def supplier_view(request):
    suppliers = Supplier.objects.all().order_by("-created_at")
    total_suppliers = suppliers.count()
    return render(
        request,
        "suppliers.html",
        {"suppliers": suppliers, "total_suppliers": total_suppliers},
    )


def add_supplier(request):
    """Handles creation of a new supplier."""
    if request.method == "POST":
        form = SupplierForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Supplier added successfully.")
            return redirect("suppliers")
    else:
        form = SupplierForm()
    return render(request, "forms/add/add_supplier.html", {"form": form})


def edit_supplier(request, pk):
    """Handles editing of an existing supplier."""
    supplier = get_object_or_404(Supplier, pk=pk)
    if request.method == "POST":
        form = SupplierForm(request.POST, instance=supplier)
        if form.is_valid():
            form.save()
            messages.success(request, "Supplier updated successfully.")
            return redirect("suppliers")
    else:
        form = SupplierForm(instance=supplier)
    return render(
        request, "forms/edit/edit_supplier.html", {"form": form, "supplier": supplier}
    )


@login_required
def view_supplier(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    return render(
        request,
        "view/view_supplier.html",
        {"supplier": supplier},
    )


@login_required
def delete_supplier(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    if request.method == "POST":
        supplier.delete()
        messages.success(request, f'Supplier "{supplier.name}" deleted successfully.')
        return redirect("suppliers")
    return redirect("view_supplier", pk=pk)


@login_required
def delete_all_suppliers(request):
    if request.method == "POST":
        for supplier in Supplier.objects.all():
            supplier.delete()  # Triggers signal
        messages.success(request, "All suppliers deleted and stock levels updated.")
    return redirect("suppliers")
