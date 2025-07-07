from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.shortcuts import redirect, render

from .models import Category, Item, ItemImage, UnitOfMeasure


@login_required
def items_view(request):
    items = Item.objects.all()
    context = {"items": items}
    return render(request, "items.html", context)


def add_item(request):
    if request.method == "POST":
        # Extract POST data
        name = request.POST.get("name")
        sku = request.POST.get("sku")
        unit_id = request.POST.get("unit")
        category_id = request.POST.get("category")
        selling_price = request.POST.get("selling_price") or None
        purchase_price = request.POST.get("purchase_price") or None
        track_inventory = request.POST.get("track_inventory") == "on"
        opening_stock = request.POST.get("opening_stock") or None
        reorder_point = request.POST.get("reorder_point") or None
        image_file = request.FILES.get("image")

        try:
            unit = UnitOfMeasure.objects.get(pk=unit_id)
        except UnitOfMeasure.DoesNotExist:
            messages.error(request, "Invalid unit selected.")
            return redirect("add_item")

        category = None
        if category_id:
            try:
                category = Category.objects.get(pk=category_id)
            except Category.DoesNotExist:
                messages.error(request, "Invalid category selected.")
                return redirect("add_item")

        # Convert numeric values
        try:
            if selling_price:
                selling_price = float(selling_price)
            if purchase_price:
                purchase_price = float(purchase_price)
            if opening_stock:
                opening_stock = int(opening_stock)
            if reorder_point:
                reorder_point = int(reorder_point)
        except ValueError:
            messages.error(request, "Invalid number entered.")
            return redirect("add_item")

        # Create item
        item = Item(
            name=name,
            sku=sku,
            unit=unit,
            category=category,
            selling_price=selling_price,
            purchase_price=purchase_price,
            track_inventory=track_inventory,
            opening_stock=opening_stock if track_inventory else None,
            current_stock=(
                opening_stock if track_inventory and opening_stock is not None else 0
            ),
            reorder_point=reorder_point if track_inventory else None,
        )

        try:
            item.full_clean()
            item.save()
        except ValidationError as e:
            messages.error(request, f"Validation error: {e}")
            return redirect("add_item")

        # Handle image upload
        if image_file:
            ItemImage.objects.create(item=item, image=image_file)

        messages.success(request, "Item created successfully.")
        return redirect("items")

    # GET method: provide unit/category options
    units = UnitOfMeasure.objects.all()
    categories = Category.objects.all()
    return render(
        request,
        "forms/add_item.html",
        {"units": units, "categories": categories},
    )
