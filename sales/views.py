from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from authentication.models import UserProfile
from inventory.utils import check_and_create_low_stock_alert
from sales.models import Customer, Sale

from .forms import CustomerForm, SaleForm
from .utils import generate_sales_number


@login_required
def sales_view(request):
    sales = Sale.objects.select_related("item").order_by("-created_at")
    total_sales = sales.count()

    context = {
        "sales": sales,
        "total_sales": total_sales,
    }
    return render(request, "sales.html", context)


@login_required
def add_sale(request):
    if request.method == "POST":
        form = SaleForm(request.POST)
        if form.is_valid():
            sale = form.save(commit=False)
            sale.user = request.user
            # Generate sales number *after* counting existing sales
            sale_number = generate_sales_number()
            sale.sales_number = sale_number  # assuming you have a sales_number field
            sale.save()
            # Check and create low stock alert if necessary
            check_and_create_low_stock_alert(sale.item)

            messages.success(
                request, f"Sale recorded successfully for {sale.item.name}."
            )
            return redirect("sales")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = SaleForm()
        # Only for preview (optional; can remove this if not displaying it in form)
        sales_number_preview = generate_sales_number()

    return render(
        request,
        "forms/add/add_sale.html",
        {
            "form": form,
            "sales_number": sales_number_preview if request.method != "POST" else None,  # type: ignore
        },
    )


@login_required
def edit_sale(request, pk):
    sale = get_object_or_404(Sale, pk=pk)

    if request.method == "POST":
        form = SaleForm(request.POST, instance=sale)
        if form.is_valid():
            form.save()

            messages.success(request, f"Sale {sale.sales_number} updated successfully.")
            return redirect("view_sale", pk=sale.pk)
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = SaleForm(instance=sale)

    return render(
        request,
        "forms/edit/edit_sale.html",
        {
            "form": form,
            "sale": sale,
        },
    )


@login_required
def view_sale(request, pk):
    sale = get_object_or_404(Sale, pk=pk)
    user_profile = (
        UserProfile.objects.filter(user=sale.user).first() if sale.user else None
    )
    context = {
        "sale": sale,
        "user_profile": user_profile,
    }
    return render(request, "view/view_sale.html", context)


@login_required
def delete_sale(request, pk):
    sale = get_object_or_404(Sale, pk=pk)
    if request.method == "POST":
        sale.delete()
        messages.success(request, f'Sale "{sale.sales_number}" deleted successfully.')
        return redirect("sales")
    return redirect("view_sale", pk=pk)


@login_required
def delete_all_sales(request):
    if request.method == "POST":
        Sale.objects.all().delete()
        messages.success(request, "All sales records deleted and stock levels reset.")
    return redirect("sales")


@login_required
def customers_view(request):
    customers = Customer.objects.all().order_by("-created_at")
    total_customers = customers.count()

    return render(
        request,
        "customers.html",
        {"customers": customers, "total_customers": total_customers},
    )


def add_customer(request):
    """Handles creation of a new customer."""
    if request.method == "POST":
        form = CustomerForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Customer added successfully.")
            return redirect("customers")
    else:
        form = CustomerForm()
    return render(request, "forms/add/add_customer.html", {"form": form})


def edit_customer(request, pk):
    """Handles editing of an existing customer."""
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == "POST":
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            messages.success(request, "Customer updated successfully.")
            return redirect("customers")
    else:
        form = CustomerForm(instance=customer)
    return render(
        request, "forms/edit/edit_customer.html", {"form": form, "customer": customer}
    )


@login_required
def view_customer(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    total_customers = Customer.objects.count()
    context = {
        "customer": customer,
        "total_customers": total_customers,
    }
    return render(
        request,
        "view/view_customer.html",
        context,
    )


@login_required
def delete_customer(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == "POST":
        customer.delete()
        messages.success(request, f'Customer "{customer.name}" deleted successfully.')
        return redirect("customers")
    return redirect("view_customer", pk=pk)


@login_required
def delete_all_customers(request):
    if request.method == "POST":
        for customer in Customer.objects.all():
            customer.delete()
        messages.success(request, "All customer records deleted.")
    return redirect("customers")
