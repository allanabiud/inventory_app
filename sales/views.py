from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from authentication.models import UserProfile
from sales.models import Sale

from .forms import SaleForm
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
            sale.save()
            messages.success(
                request, f"Sale recorded successfully for {sale.item.name}."
            )
            return redirect("sales")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        # Pre-create the sales number just to show
        sales_number_preview = generate_sales_number()
        form = SaleForm()

    context = {
        "form": form,
        "title": "Record a New Sale",
        "sales_number": sales_number_preview,  # type: ignore
    }
    return render(
        request,
        "forms/add/add_sale.html",
        context,
    )


@login_required
def edit_sale(request, pk):
    sale = get_object_or_404(Sale, id=pk)

    if request.method == "POST":
        form = SaleForm(request.POST, instance=sale)
        if form.is_valid():
            form.save()
            messages.success(request, "Sale updated successfully.")
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
