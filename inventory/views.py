from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.db.models import Count
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from authentication.models import UserProfile

from .models import Category, InventoryAdjustment, Item, ItemImage, UnitOfMeasure
from .utils import generate_item_csv_template, process_item_csv_upload


@login_required
def items_view(request):
    """
    Displays a list of all items.
    Requires user to be logged in.
    """
    items = Item.objects.all()
    total_items = Item.objects.count()
    context = {"items": items, "total_items": total_items}
    return render(request, "items.html", context)


@login_required
def add_item(request):
    """
    Handles the addition of new items.
    Processes form submission for creating a new item, including validation
    and image upload. Re-renders the form with errors if validation fails.
    Requires user to be logged in.
    """
    errors = {}
    form_data = {}

    if request.method == "POST":
        # 1. Retrieve Data from POST & FILES
        name = request.POST.get("name", "").strip()
        # SKU is received as a single combined string from the hidden field
        sku = request.POST.get("sku", "").strip()

        unit_id = request.POST.get("unit")
        category_id = request.POST.get("category")
        selling_price_str = request.POST.get("selling_price")
        purchase_price_str = request.POST.get("purchase_price")

        opening_stock_str = request.POST.get("opening_stock")
        current_stock_str = request.POST.get("current_stock")
        reorder_point_str = request.POST.get("reorder_point")

        image_file = request.FILES.get("image")

        split_sku = sku.split("-", 1)  # Split only on the first '-'
        sku_prefix_for_form = split_sku[0] if split_sku else ""
        sku_number_for_form = split_sku[1] if len(split_sku) > 1 else ""

        form_data = {
            "name": name,
            "sku_prefix": sku_prefix_for_form,  # For re-populating the form's prefix field
            "sku_number": sku_number_for_form,  # For re-populating the form's number field
            "sku": sku,  # The actual combined SKU
            "unit": unit_id,
            "category": category_id,
            "selling_price": selling_price_str,
            "purchase_price": purchase_price_str,
            "opening_stock": opening_stock_str,
            "current_stock": current_stock_str,
            "reorder_point": reorder_point_str,
            "image_exists": bool(
                image_file
            ),  # For previewing the uploaded image on error
        }

        # 2. Validation
        validated_unit = None
        validated_category = None
        validated_selling_price = None
        validated_purchase_price = None
        validated_opening_stock = None
        validated_current_stock = None
        validated_reorder_point = None

        if not name:
            errors["name"] = ["Name is required."]
        if not sku:
            errors["sku"] = ["SKU is required."]  # Validation for the combined SKU

        if "sku" not in errors and sku and Item.objects.filter(sku=sku).exists():
            errors["sku"] = ["An item with this SKU already exists."]

        if not unit_id:
            errors["unit"] = ["Unit of Measure is required."]
        else:
            try:
                validated_unit = UnitOfMeasure.objects.get(pk=unit_id)
            except UnitOfMeasure.DoesNotExist:
                errors["unit"] = ["Invalid Unit of Measure selected."]

        if category_id:  # Category is nullable
            try:
                validated_category = Category.objects.get(pk=category_id)
            except Category.DoesNotExist:
                errors["category"] = ["Invalid Category selected."]

        # Validate and convert pricing fields
        try:
            if selling_price_str:
                validated_selling_price = Decimal(selling_price_str)
                if validated_selling_price < 0:
                    errors.setdefault("selling_price", []).append(
                        "Selling price cannot be negative."
                    )
            else:
                validated_selling_price = None  # Set to None if blank
        except (ValueError, InvalidOperation):
            errors.setdefault("selling_price", []).append(
                "Please enter a valid selling price."
            )

        try:
            if purchase_price_str:
                validated_purchase_price = Decimal(purchase_price_str)
                if validated_purchase_price < 0:
                    errors.setdefault("purchase_price", []).append(
                        "Purchase price cannot be negative."
                    )
            else:
                validated_purchase_price = None  # Set to None if blank
        except (ValueError, InvalidOperation):
            errors.setdefault("purchase_price", []).append(
                "Please enter a valid purchase price."
            )

        # Validate and convert inventory fields (now independent, no 'track_inventory' dependency)
        try:
            if opening_stock_str:  # opening_stock is nullable
                validated_opening_stock = int(opening_stock_str)
                if validated_opening_stock < 0:
                    errors.setdefault("opening_stock", []).append(
                        "Opening stock cannot be negative."
                    )
            else:
                validated_opening_stock = None
        except ValueError:
            errors.setdefault("opening_stock", []).append(
                "Please enter a valid number for Opening Stock."
            )

        try:
            if (
                current_stock_str
            ):  # current_stock has default=0 but can be explicitly set
                validated_current_stock = int(current_stock_str)
                if validated_current_stock < 0:
                    errors.setdefault("current_stock", []).append(
                        "Current stock cannot be negative."
                    )
            else:
                validated_current_stock = 0  # Default if not provided
        except ValueError:
            errors.setdefault("current_stock", []).append(
                "Please enter a valid number for Current Stock."
            )

        try:
            if reorder_point_str:  # reorder_point is nullable
                validated_reorder_point = int(reorder_point_str)
                if validated_reorder_point < 0:
                    errors.setdefault("reorder_point", []).append(
                        "Reorder point cannot be negative."
                    )
            else:
                validated_reorder_point = None
        except ValueError:
            errors.setdefault("reorder_point", []).append(
                "Please enter a valid number for Reorder Point."
            )

        if errors:
            # Add general messages for errors for user feedback
            for field, error_list in errors.items():
                for error_msg in error_list:
                    # Avoid showing 'sku_prefix', 'sku_number' specific errors if the combined 'sku' error is sufficient
                    if field not in [
                        "sku_prefix",
                        "sku_number",
                    ]:  # Only show general messages for actual model fields
                        messages.error(
                            request, f"{field.replace('_', ' ').title()}: {error_msg}"
                        )
            messages.error(request, "Please correct the errors below.")

            units = UnitOfMeasure.objects.all()
            categories = Category.objects.all()
            context = {
                "units": units,
                "categories": categories,
                "form_data": form_data,
                "errors": errors,  # Pass detailed errors for field-specific invalid-feedback
            }
            return render(request, "forms/add_item.html", context)

        # 3. Create and Save Item if no errors
        try:
            with transaction.atomic():  # Use transaction for atomicity
                item = Item(
                    name=name,
                    sku=sku,  # Use the combined SKU
                    unit=validated_unit,
                    category=validated_category,
                    selling_price=validated_selling_price,
                    purchase_price=validated_purchase_price,
                    opening_stock=validated_opening_stock,
                    current_stock=validated_current_stock,
                    reorder_point=validated_reorder_point,
                )
                item.full_clean()  # Perform model-level validation (e.g., unique SKU check)
                item.save()

                if image_file:
                    ItemImage.objects.create(item=item, image=image_file)

                messages.success(request, f'Item "{item.name}" added successfully!')
                return redirect(
                    "items"
                )  # Adjust to your actual success URL, e.g., 'item_list'

        except IntegrityError:
            # This catches database-level errors, e.g., unique constraint violation for SKU
            errors["sku"] = [
                "An item with this SKU already exists (database conflict)."
            ]
            messages.error(
                request,
                "A database error occurred, possibly a duplicate SKU. Please try again.",
            )

            units = UnitOfMeasure.objects.all()
            categories = Category.objects.all()
            context = {
                "units": units,
                "categories": categories,
                "form_data": form_data,
                "errors": errors,
            }
            return render(request, "forms/add_item.html", context)

        except ValidationError as e:
            # This catches model's clean() method errors (though our clean is empty now)
            # and potentially default Django form validation if using ModelForms
            for field, field_errors in e.message_dict.items():
                errors[field] = (
                    errors.get(field, []) + field_errors
                )  # Append to existing errors
                for error_msg in field_errors:
                    messages.error(
                        request, f"{field.replace('_', ' ').title()}: {error_msg}"
                    )
            messages.error(request, "Please correct the errors below.")

            units = UnitOfMeasure.objects.all()
            categories = Category.objects.all()
            context = {
                "units": units,
                "categories": categories,
                "form_data": form_data,
                "errors": errors,
            }
            return render(request, "forms/add_item.html", context)

        except Exception as e:
            # Catch any other unexpected errors
            messages.error(request, f"An unexpected error occurred: {e}")
            import traceback

            traceback.print_exc()  # For debugging: print full traceback to console/logs

            units = UnitOfMeasure.objects.all()
            categories = Category.objects.all()
            context = {
                "units": units,
                "categories": categories,
                "form_data": form_data,
                "errors": {"general": [f"An unexpected error occurred: {e}"]},
            }
            return render(request, "forms/add_item.html", context)

    else:  # GET request: Render empty form or with default values
        form_data = {
            "name": "",
            "sku_prefix": "SKU",  # Default prefix
            "sku_number": "",
            "sku": "",  # This will be set by JS
            "unit": "",
            "category": "",
            "selling_price": "",
            "purchase_price": "",
            "opening_stock": "",
            "current_stock": "",
            "reorder_point": "",
            "image_exists": False,  # No image on initial load
        }

    units = UnitOfMeasure.objects.all()
    categories = Category.objects.all()

    context = {
        "units": units,
        "categories": categories,
        "form_data": form_data,
        "errors": errors,  # Will be empty on GET request
    }
    return render(request, "forms/add_item.html", context)


@login_required
def edit_item(request, pk):
    item = get_object_or_404(Item, pk=pk)
    current_item_image = item.images.first()
    errors = {}
    form_data = {}

    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        sku_prefix = request.POST.get("sku_prefix", "").strip()
        sku_number = request.POST.get("sku_number", "").strip()
        unit_id = request.POST.get("unit")
        category_id = request.POST.get("category")

        selling_price_str = request.POST.get("selling_price", "").strip()
        purchase_price_str = request.POST.get("purchase_price", "").strip()

        opening_stock_str = request.POST.get("opening_stock", "").strip()
        current_stock_str = request.POST.get("current_stock", "").strip()
        reorder_point_str = request.POST.get("reorder_point", "").strip()

        new_image_file = request.FILES.get("image")
        clear_image_requested = request.POST.get("clear_image") == "true"

        form_data = request.POST.copy()

        # --- Validation ---

        if not name:
            errors.setdefault("name", []).append("Item name is required.")

        # SKU logic
        combined_sku = ""
        if sku_prefix and sku_number:
            combined_sku = f"{sku_prefix}-{sku_number}"
        elif sku_prefix:
            combined_sku = sku_prefix
        elif sku_number:
            errors.setdefault("sku_prefix", []).append("SKU Prefix is required.")
            errors.setdefault("sku_number", []).append("SKU Prefix is required.")
        else:
            errors.setdefault("sku_prefix", []).append("SKU is required.")
            errors.setdefault("sku_number", []).append("SKU is required.")

        if combined_sku:
            existing_items = Item.objects.filter(sku=combined_sku).exclude(pk=item.pk)
            if existing_items.exists():
                errors.setdefault("sku", []).append(
                    "An item with this SKU already exists."
                )

        # Unit
        selected_unit = None
        if not unit_id:
            errors.setdefault("unit", []).append("Unit of Measure is required.")
        else:
            try:
                selected_unit = UnitOfMeasure.objects.get(pk=unit_id)
            except UnitOfMeasure.DoesNotExist:
                errors.setdefault("unit", []).append("Invalid Unit selected.")

        # Category
        selected_category = None
        if category_id:
            try:
                selected_category = Category.objects.get(pk=category_id)
            except Category.DoesNotExist:
                errors.setdefault("category", []).append("Invalid Category selected.")

        # Prices
        selling_price = None
        if selling_price_str:
            try:
                selling_price = Decimal(selling_price_str)
                if selling_price < 0:
                    errors.setdefault("selling_price", []).append(
                        "Selling Price cannot be negative."
                    )
            except InvalidOperation:
                errors.setdefault("selling_price", []).append("Invalid Selling Price.")
        else:
            errors.setdefault("selling_price", []).append("Selling Price is required.")

        purchase_price = None
        if purchase_price_str:
            try:
                purchase_price = Decimal(purchase_price_str)
                if purchase_price < 0:
                    errors.setdefault("purchase_price", []).append(
                        "Purchase Price cannot be negative."
                    )
            except InvalidOperation:
                errors.setdefault("purchase_price", []).append(
                    "Invalid Purchase Price."
                )
        else:
            errors.setdefault("purchase_price", []).append(
                "Purchase Price is required."
            )

        # Inventory fields
        opening_stock = None
        current_stock = None
        reorder_point = None

        # Opening Stock
        if opening_stock_str:
            try:
                opening_stock = int(opening_stock_str)
                if opening_stock < 0:
                    errors.setdefault("opening_stock", []).append(
                        "Opening Stock cannot be negative."
                    )
            except ValueError:
                errors.setdefault("opening_stock", []).append(
                    "Opening Stock must be a whole number."
                )

        # Current Stock
        if current_stock_str:
            try:
                current_stock = int(current_stock_str)
                if current_stock < 0:
                    errors.setdefault("current_stock", []).append(
                        "Current Stock cannot be negative."
                    )
            except ValueError:
                errors.setdefault("current_stock", []).append(
                    "Current Stock must be a whole number."
                )

        # Reorder Point
        if reorder_point_str:
            try:
                reorder_point = int(reorder_point_str)
                if reorder_point < 0:
                    errors.setdefault("reorder_point", []).append(
                        "Reorder Point cannot be negative."
                    )
            except ValueError:
                errors.setdefault("reorder_point", []).append(
                    "Reorder Point must be a whole number."
                )

        # --- Save if No Errors ---
        if not errors:
            try:
                with transaction.atomic():
                    item.name = name
                    item.sku = combined_sku
                    item.unit = selected_unit
                    item.category = selected_category
                    item.selling_price = selling_price
                    item.purchase_price = purchase_price
                    item.opening_stock = opening_stock
                    item.current_stock = current_stock
                    item.reorder_point = reorder_point
                    item.save()

                    # Clear image if requested
                    if clear_image_requested and current_item_image:
                        current_item_image.image.delete(save=False)
                        current_item_image.delete()
                        current_item_image = None

                    # Upload new image
                    if new_image_file:
                        if current_item_image:
                            current_item_image.image.delete(save=False)
                            current_item_image.delete()
                        ItemImage.objects.create(item=item, image=new_image_file)

                messages.success(request, f'Item "{item.name}" updated successfully!')
                return redirect("view_item", pk=item.pk)

            except Exception as e:
                messages.error(request, f"An unexpected error occurred: {e}")
                errors.setdefault("general", []).append(
                    f"Server error: {e}. Please try again."
                )

        current_image_url = (
            current_item_image.image.url
            if current_item_image and current_item_image.image
            else None
        )
        image_exists = bool(current_item_image and current_item_image.image)
        if clear_image_requested:
            current_image_url = None
            image_exists = False

        context = {
            "item": item,
            "form_data": form_data,
            "errors": errors,
            "units": UnitOfMeasure.objects.all(),
            "categories": Category.objects.all(),
            "current_image_url": current_image_url,
            "image_exists": image_exists,
        }

    else:  # GET
        form_data = {
            "name": item.name,
            "sku_prefix": item.sku.split("-", 1)[0] if item.sku else "",
            "sku_number": (
                item.sku.split("-", 1)[1] if item.sku and "-" in item.sku else ""
            ),
            "unit": item.unit.pk if item.unit else "",
            "category": item.category.pk if item.category else "",
            "selling_price": item.selling_price,
            "purchase_price": item.purchase_price,
            "opening_stock": item.opening_stock,
            "current_stock": item.current_stock,
            "reorder_point": item.reorder_point,
        }
        current_image_url = (
            current_item_image.image.url
            if current_item_image and current_item_image.image
            else None
        )
        image_exists = bool(current_item_image and current_item_image.image)

        context = {
            "item": item,
            "form_data": form_data,
            "errors": errors,
            "units": UnitOfMeasure.objects.all(),
            "categories": Category.objects.all(),
            "current_image_url": current_image_url,
            "image_exists": image_exists,
        }

    return render(request, "forms/edit_item.html", context)


@login_required
def view_item(request, pk):
    item = get_object_or_404(Item, pk=pk)

    context = {
        "item": item,
    }
    return render(request, "view/view_item.html", context)


@login_required
def delete_item(request, pk):
    item = get_object_or_404(Item, pk=pk)
    if request.method == "POST":
        item.delete()
        messages.success(request, f'Item "{item.name}" deleted successfully.')
        return redirect("items")
    return redirect("view_item", pk=pk)  # If not POST, redirect back to item detail


@login_required
def delete_all_items(request):
    """
    View to delete all Item records from the database.
    Requires a POST request for security.
    """
    if request.method == "POST":
        try:
            with transaction.atomic():
                # Delete all Item records
                # This will also cascade delete related ItemImage and InventoryAdjustment records
                # due to CASCADE on_delete in those models.
                deleted_count, _ = Item.objects.all().delete()
                messages.success(
                    request, f"Successfully deleted {deleted_count} items."
                )
        except Exception as e:
            messages.error(request, f"An error occurred while deleting items: {e}")

    return redirect("items")  # Redirect back to the items list page


@login_required
def generate_csv_template_view(request):
    """
    View to generate and download a CSV template for item import.
    """
    # Generate the CSV content using the utility function
    csv_buffer = generate_item_csv_template()

    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(csv_buffer.getvalue(), content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="item_template.csv"'

    return response


@login_required
def import_items_view(request):
    """
    View to handle displaying the CSV import form and processing uploaded files.
    """
    if request.method == "POST":
        csv_file = request.FILES.get("csv_file")

        if not csv_file:
            messages.error(request, "No CSV file was uploaded.")
            return redirect("import_items")  # Redirect back to the import page

        # Basic file type validation
        if not csv_file.name.endswith(".csv"):
            messages.error(request, "Invalid file type. Please upload a CSV file.")
            return redirect("import_items")

        try:
            # Call the utility function to process the CSV
            import_results = process_item_csv_upload(csv_file)

            total_rows = import_results["total_rows"]
            successful_imports = import_results["successful_imports"]
            failed_imports = import_results["failed_imports"]
            errors = import_results["errors"]

            if successful_imports > 0:
                messages.success(
                    request,
                    f"Successfully imported/updated {successful_imports} out of {total_rows} items.",
                )

            if failed_imports > 0:
                error_message = f"Failed to import/update {failed_imports} items. See details below:"
                messages.error(request, error_message)
                # Store detailed errors in session or pass directly to context if re-rendering
                # For simplicity, we'll add them as individual messages here.
                for error_detail in errors:
                    row_num = error_detail["row_num"]
                    error_data = error_detail["data"]
                    error_messages = "; ".join(error_detail["messages"])
                    messages.warning(
                        request,
                        f"Row {row_num}: {error_messages} (Data: {error_data.get('name', 'N/A')}, SKU: {error_data.get('sku', 'N/A')})",
                    )

            if successful_imports == 0 and failed_imports == 0 and total_rows > 0:
                messages.info(
                    request, "No items were processed. Check CSV format and content."
                )
            elif total_rows == 0:
                messages.info(request, "The uploaded CSV file was empty.")

            return redirect("import_items")  # Redirect back to show messages

        except Exception as e:
            messages.error(
                request, f"An unexpected error occurred during CSV processing: {e}"
            )
            return redirect("import_items")

    # For GET requests, just render the form
    return render(request, "forms/import_form.html")


## CATEGORIES
@login_required
def categories_view(request):
    categories = Category.objects.all().annotate(item_count=Count("item"))
    total_categories = categories.count()
    return render(
        request,
        "categories.html",
        {
            "categories": categories,
            "total_categories": total_categories,
        },
    )


@login_required
def add_category(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        description = request.POST.get("description", "").strip()
        errors = {}

        # Validation
        if not name:
            errors["name"] = ["Category name is required."]
        elif Category.objects.filter(name__iexact=name).exists():
            errors["name"] = ["A category with this name already exists."]

        if errors:
            return render(
                request,
                "forms/add_category.html",
                {
                    "form_data": {
                        "name": name,
                        "description": description,
                    },
                    "errors": errors,
                },
            )

        # Save category
        Category.objects.create(name=name, description=description)
        messages.success(request, "Category added successfully.")
        return redirect("categories")

    return render(request, "forms/add_category.html")


@login_required
def edit_category(request, pk):
    category = get_object_or_404(Category, pk=pk)
    current_category_description = category.description
    errors = {}
    form_data = {}

    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        description = request.POST.get("description", "").strip()
        errors = {}

        # Validation
        if not name:
            errors["name"] = ["Category name is required."]
        # elif Category.objects.filter(name__iexact=name).exists():
        elif (
            Category.objects.exclude(pk=category.pk).filter(name__iexact=name).exists()
        ):
            errors["name"] = ["A category with this name already exists."]

        if errors:
            return render(
                request,
                "forms/edit_category.html",
                {
                    "form_data": {
                        "name": name,
                        "description": description,
                    },
                    "errors": errors,
                },
            )

        # Save category
        category.name = name
        category.description = description
        category.save()

        messages.success(request, "Category updated successfully.")
        return redirect("view_category", pk=pk)

    else:  # GET
        form_data = {
            "name": category.name,
            "description": current_category_description,
        }

    return render(
        request,
        "forms/edit_category.html",
        {
            "category": category,
            "form_data": form_data,
            "errors": errors,
        },
    )


@login_required
def view_category(request, pk):
    category = get_object_or_404(Category, pk=pk)
    items = Item.objects.filter(category=category).order_by("-created_at")
    return render(
        request,
        "view/view_category.html",
        {
            "category": category,
            "items": items,
        },
    )


@login_required
def delete_category(request, pk):
    category = get_object_or_404(Category, pk=pk)

    if request.method == "POST":
        category_name = category.name
        # Remove the category from items but keep the items
        category.delete()
        messages.success(request, f'Category "{category_name}" has been deleted.')
        return redirect("categories")

    messages.error(request, "Invalid request method.")
    return redirect("view_category", pk=pk)


@login_required
def delete_all_categories(request):
    """
    View to delete all Category records from the database.
    Requires a POST request for security.
    """
    if request.method == "POST":
        try:
            # Delete all Category records
            # This will also cascade delete related Item records due to CASCADE on_delete in Category
            deleted_count, _ = Category.objects.all().delete()
            messages.success(
                request, f"Successfully deleted {deleted_count} categories."
            )
        except Exception as e:
            messages.error(request, f"An error occurred while deleting categories: {e}")

    return redirect("categories")  # Redirect back to the categories list page


## UNITS
@login_required
def units_view(request):
    units = UnitOfMeasure.objects.all().annotate(item_count=Count("item"))
    total_units = units.count()
    all_units_empty = all(unit.item_count == 0 for unit in units)

    return render(
        request,
        "units.html",
        {
            "units": units,
            "total_units": total_units,
            "all_units_empty": all_units_empty,
        },
    )


@login_required
def add_unit(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        abbreviation = request.POST.get("abbreviation", "").strip()
        description = request.POST.get("description", "").strip()
        errors = {}

        # Validation
        if not name:
            errors["name"] = ["Unit name is required."]
        elif UnitOfMeasure.objects.filter(name__iexact=name).exists():
            errors["name"] = ["A unit with this name already exists."]

        if errors:
            return render(
                request,
                "forms/add_unit.html",
                {
                    "form_data": {
                        "name": name,
                        "abbreviation": abbreviation,
                        "description": description,
                    },
                    "errors": errors,
                },
            )

        # Save unit
        UnitOfMeasure.objects.create(
            name=name, abbreviation=abbreviation, description=description
        )
        messages.success(request, "Unit added successfully.")
        return redirect("units")

    return render(request, "forms/add_unit.html")


@login_required
def edit_unit(request, pk):
    unit = get_object_or_404(UnitOfMeasure, pk=pk)
    errors = {}
    form_data = {}

    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        abbreviation = request.POST.get("abbreviation", "").strip()
        description = request.POST.get("description", "").strip()

        # Validation
        if not name:
            errors["name"] = ["Unit name is required."]
        elif (
            UnitOfMeasure.objects.exclude(pk=unit.pk).filter(name__iexact=name).exists()
        ):
            errors["name"] = ["A unit with this name already exists."]

        if errors:
            return render(
                request,
                "forms/edit_unit.html",
                {
                    "unit": unit,
                    "form_data": {
                        "name": name,
                        "abbreviation": abbreviation,
                        "description": description,
                    },
                    "errors": errors,
                },
            )

        # Save changes
        unit.name = name
        unit.abbreviation = abbreviation or None
        unit.description = description or None
        unit.save()

        messages.success(request, "Unit updated successfully.")
        return redirect("view_unit", pk=pk)

    else:
        form_data = {
            "name": unit.name,
            "abbreviation": unit.abbreviation,
            "description": unit.description,
        }

    return render(
        request,
        "forms/edit_unit.html",
        {
            "unit": unit,
            "form_data": form_data,
            "errors": errors,
        },
    )


@login_required
def view_unit(request, pk):
    unit = get_object_or_404(UnitOfMeasure, pk=pk)
    items = Item.objects.filter(unit=unit)
    context = {
        "unit": unit,
        "items": items,
    }
    return render(request, "view/view_unit.html", context)


@login_required
def delete_unit(request, pk):
    unit = get_object_or_404(UnitOfMeasure, pk=pk)
    if request.method == "POST":
        unit.delete()
        messages.success(request, f'Unit "{unit.name}" was deleted successfully.')
        return redirect("units")
    return redirect("view_unit", pk=pk)  # If not POST, redirect back to unit detail


@login_required
def delete_all_units(request):
    """
    View to delete all Unit records from the database.
    Requires a POST request for security.
    """
    if request.method == "POST":
        try:
            # Delete all Unit records
            # This will also cascade delete related Item records due to CASCADE on_delete in Unit
            deleted_count, _ = UnitOfMeasure.objects.all().delete()
            messages.success(request, f"Successfully deleted {deleted_count} units.")
        except Exception as e:
            messages.error(request, f"An error occurred while deleting units: {e}")

    return redirect("units")  # Redirect back to the units list page


## INVENTORY ADJUSTMENTS
@login_required
def inventory_adjustments(request):
    adjustments = InventoryAdjustment.objects.select_related(
        "item", "item__unit", "user"
    ).order_by("-date")

    context = {
        "adjustments": adjustments,
        "total_adjustments": adjustments.count(),
    }

    return render(request, "inventory_adjustments.html", context)


@login_required
def add_adjustment(request):
    items = Item.objects.all()
    reason_choices = InventoryAdjustment.REASON_CHOICES
    errors = {}
    form_data = {}

    if request.method == "POST":
        item_id = request.POST.get("item")
        adjustment_type = request.POST.get("adjustment_type")
        quantity_adjusted = request.POST.get("quantity_adjusted")
        cost_price = request.POST.get("cost_price")
        reason = request.POST.get("reason")
        description = request.POST.get("description")

        # Preserve form values
        form_data = {
            "item": item_id,
            "adjustment_type": adjustment_type,
            "quantity_adjusted": quantity_adjusted,
            "cost_price": cost_price,
            "reason": reason,
            "description": description,
        }

        # Validation
        if not item_id:
            errors["item"] = ["Please select an item."]
        else:
            try:
                item = Item.objects.get(pk=item_id)
            except Item.DoesNotExist:
                errors["item"] = ["Invalid item selected."]

        if adjustment_type not in dict(InventoryAdjustment.ADJUSTMENT_TYPES):
            errors["adjustment_type"] = ["Invalid adjustment type."]

        if (
            not quantity_adjusted
            or not quantity_adjusted.isdigit()
            or int(quantity_adjusted) <= 0
        ):
            errors["quantity_adjusted"] = ["Enter a valid quantity."]

        if cost_price:
            try:
                float(cost_price)
            except ValueError:
                errors["cost_price"] = ["Enter a valid cost price."]

        if reason not in dict(reason_choices):
            errors["reason"] = ["Please select a valid reason."]

        if not errors:
            try:
                adj = InventoryAdjustment.objects.create(
                    item=item,
                    adjustment_type=adjustment_type,
                    quantity_adjusted=int(quantity_adjusted),
                    cost_price=cost_price or None,
                    reason=reason,
                    description=description or "",
                    user=request.user,
                    date=timezone.now(),
                )
                messages.success(request, "Inventory adjustment recorded successfully.")
                return redirect("inventory_adjustments")
            except ValidationError as ve:
                errors["quantity_adjusted"] = [str(ve.message)]

    return render(
        request,
        "forms/add_adjustment.html",
        {
            "items": items,
            "reason_choices": reason_choices,
            "errors": errors,
            "form_data": form_data,
        },
    )


@login_required
def view_adjustment(request, pk):
    adjustment = get_object_or_404(InventoryAdjustment, pk=pk)
    user_profile = (
        UserProfile.objects.filter(user=adjustment.user).first()
        if adjustment.user
        else None
    )
    context = {
        "adjustment": adjustment,
        "user_profile": user_profile,
    }
    return render(request, "view/view_adjustment.html", context)


@login_required
def edit_adjustment(request, pk):
    adjustment = get_object_or_404(InventoryAdjustment, pk=pk)
    items = Item.objects.all()
    reason_choices = InventoryAdjustment.REASON_CHOICES

    if request.method == "POST":
        form_data = {
            "item": request.POST.get("item"),
            "adjustment_type": request.POST.get("adjustment_type"),
            "quantity_adjusted": request.POST.get("quantity_adjusted"),
            "cost_price": request.POST.get("cost_price"),
            "reason": request.POST.get("reason"),
            "description": request.POST.get("description"),
        }

        errors = {}

        # Validate item
        try:
            item = Item.objects.get(pk=form_data["item"])
        except (Item.DoesNotExist, ValueError, TypeError):
            errors["item"] = ["Invalid item selected."]
            item = None

        # Validate adjustment type
        if form_data["adjustment_type"] not in dict(
            InventoryAdjustment.ADJUSTMENT_TYPES
        ):
            errors["adjustment_type"] = ["Invalid adjustment type."]

        # Validate quantity
        try:
            quantity = int(form_data["quantity_adjusted"])
            if quantity <= 0:
                raise ValueError
        except (ValueError, TypeError):
            errors["quantity_adjusted"] = ["Enter a valid positive integer."]

        # Validate cost price
        cost_price = None
        if form_data["cost_price"]:
            try:
                cost_price = float(form_data["cost_price"])
                if cost_price < 0:
                    raise ValueError
            except ValueError:
                errors["cost_price"] = ["Enter a valid non-negative number."]

        # Validate reason
        if form_data["reason"] not in dict(reason_choices):
            errors["reason"] = ["Select a valid reason."]

        if errors:
            return render(
                request,
                "forms/edit_adjustment.html",
                {
                    "adjustment": adjustment,
                    "items": items,
                    "reason_choices": reason_choices,
                    "form_data": form_data,
                    "errors": errors,
                },
            )

        # Update and save adjustment (model handles stock correction)
        adjustment.item = item
        adjustment.adjustment_type = form_data["adjustment_type"]
        adjustment.quantity_adjusted = quantity
        adjustment.cost_price = cost_price
        adjustment.reason = form_data["reason"]
        adjustment.description = form_data["description"]
        adjustment.save()  # Let the model handle reversing and applying the change

        messages.success(request, "Inventory adjustment updated successfully.")
        return redirect("view_adjustment", pk=adjustment.pk)

    # Initial form data
    form_data = {
        "item": adjustment.item.id,
        "adjustment_type": adjustment.adjustment_type,
        "quantity_adjusted": adjustment.quantity_adjusted,
        "cost_price": adjustment.cost_price,
        "reason": adjustment.reason,
        "description": adjustment.description,
    }

    return render(
        request,
        "forms/edit_adjustment.html",
        {
            "adjustment": adjustment,
            "items": items,
            "reason_choices": reason_choices,
            "form_data": form_data,
            "errors": {},
        },
    )


@login_required
def delete_adjustment(request, pk):
    adjustment = get_object_or_404(InventoryAdjustment, pk=pk)

    # Reverse stock change
    if adjustment.adjustment_type == "INCREASE":
        adjustment.item.current_stock -= adjustment.quantity_adjusted
    elif adjustment.adjustment_type == "DECREASE":
        adjustment.item.current_stock += adjustment.quantity_adjusted
    adjustment.item.save()

    adjustment.delete()
    messages.success(request, "Inventory adjustment deleted successfully.")
    return redirect("inventory_adjustments")


@login_required
def delete_all_adjustments(request):
    if request.method == "POST":
        adjustments = InventoryAdjustment.objects.select_related("item")

        for adjustment in adjustments:
            item = adjustment.item

            # Reverse stock change
            if adjustment.adjustment_type == "INCREASE":
                item.current_stock -= adjustment.quantity_adjusted
            elif adjustment.adjustment_type == "DECREASE":
                item.current_stock += adjustment.quantity_adjusted

            item.save()
            adjustment.delete()

        messages.success(
            request, "All inventory adjustments deleted and stock levels updated."
        )
    return redirect("inventory_adjustments")
