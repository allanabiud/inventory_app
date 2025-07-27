from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.db.models import Count
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from authentication.models import UserProfile
from sales.models import Sale

from .forms import CategoryForm, InventoryAdjustmentForm, UnitOfMeasureForm
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
            "sku_prefix": sku_prefix_for_form,
            "sku_number": sku_number_for_form,
            "sku": sku,
            "unit": unit_id,
            "category": category_id,
            "selling_price": selling_price_str,
            "purchase_price": purchase_price_str,
            "opening_stock": opening_stock_str,
            "current_stock": current_stock_str,
            "reorder_point": reorder_point_str,
            "image_exists": bool(image_file),
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
        elif len(name) < 3:
            errors["name"] = ["Name must be at least 3 characters long."]
        if not sku:
            errors["sku"] = ["SKU is required."]

        # Check SKU uniqueness only if it's not already empty/invalid
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
                validated_selling_price = None
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
                validated_purchase_price = None
        except (ValueError, InvalidOperation):
            errors.setdefault("purchase_price", []).append(
                "Please enter a valid purchase price."
            )

        # Validate and convert inventory fields
        try:
            if opening_stock_str:
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
            if current_stock_str:
                validated_current_stock = int(current_stock_str)
                if validated_current_stock < 0:
                    errors.setdefault("current_stock", []).append(
                        "Current stock cannot be negative."
                    )
            else:
                validated_current_stock = 0
        except ValueError:
            errors.setdefault("current_stock", []).append(
                "Please enter a valid number for Current Stock."
            )

        try:
            if reorder_point_str:
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
            # ONLY send ONE general error message if there are any field-specific errors
            messages.error(request, "Please correct the errors below.")

            units = UnitOfMeasure.objects.all()
            categories = Category.objects.all()
            context = {
                "units": units,
                "categories": categories,
                "form_data": form_data,
                "errors": errors,  # Pass detailed errors for field-specific invalid-feedback
            }
            return render(request, "forms/add/add_item.html", context)

        # 3. Create and Save Item if no errors
        try:
            with transaction.atomic():
                item = Item(
                    name=name,
                    sku=sku,
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
            # This specific error is often better handled by a direct `Item.objects.filter(sku=sku).exists()` check
            # earlier, but it's good to have this as a fallback.
            errors["sku"] = [
                "An item with this SKU already exists (database conflict)."
            ]
            messages.error(
                request,
                "A database error occurred, possibly a duplicate SKU. Please correct the highlighted field.",  # More specific message
            )
            units = UnitOfMeasure.objects.all()
            categories = Category.objects.all()
            context = {
                "units": units,
                "categories": categories,
                "form_data": form_data,
                "errors": errors,
            }
            return render(request, "forms/add/add_item.html", context)

        except ValidationError as e:
            all_validation_errors = []
            for field, field_errors in e.message_dict.items():
                errors[field] = (
                    errors.get(field, []) + field_errors
                )  # Ensure field-specific errors are still passed to context
                for error_msg in field_errors:
                    all_validation_errors.append(
                        f"{field.replace('_', ' ').title()}: {error_msg}"
                    )

            if all_validation_errors:
                messages.error(
                    request,
                    "Please correct the following issues: "
                    + "; ".join(all_validation_errors),
                )
            else:
                messages.error(request, "Please correct the errors below.")

            units = UnitOfMeasure.objects.all()
            categories = Category.objects.all()
            context = {
                "units": units,
                "categories": categories,
                "form_data": form_data,
                "errors": errors,
            }
            return render(request, "forms/add/add_item.html", context)

        except Exception:
            # Catch any other unexpected errors
            messages.error(
                request, "An unexpected server error occurred. Please try again."
            )  # Generic user message
            import traceback

            traceback.print_exc()  # For debugging: print full traceback to console/logs

            units = UnitOfMeasure.objects.all()
            categories = Category.objects.all()
            context = {
                "units": units,
                "categories": categories,
                "form_data": form_data,
                "errors": {
                    "general": ["An unexpected error occurred."]
                },  # Provide a generic error for frontend in 'errors'
            }
            return render(request, "forms/add/add_item.html", context)

    else:  # GET request: Render empty form or with default values
        form_data = {
            "name": "",
            "sku_prefix": "SKU",
            "sku_number": "",
            "sku": "",
            "unit": "",
            "category": "",
            "selling_price": "",
            "purchase_price": "",
            "opening_stock": "",
            "current_stock": "",
            "reorder_point": "",
            "image_exists": False,
        }

    units = UnitOfMeasure.objects.all()
    categories = Category.objects.all()

    context = {
        "units": units,
        "categories": categories,
        "form_data": form_data,
        "errors": errors,  # Will be empty on GET request
    }
    return render(request, "forms/add/add_item.html", context)


@login_required
def edit_item(request, pk):
    item = get_object_or_404(Item, pk=pk)
    current_item_image = item.images.first()  # type: ignore
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
        reorder_point_str = request.POST.get("reorder_point", "").strip()

        new_image_file = request.FILES.get("image")
        clear_image_requested = request.POST.get("clear_image") == "true"

        # Use request.POST directly for form_data to retain all submitted values
        # This is important for re-populating the form fields accurately on error
        form_data = request.POST.copy()

        # --- Validation ---

        if not name:
            errors.setdefault("name", []).append("Item name is required.")
        elif len(name) < 3:
            errors.setdefault("name", []).append(
                "Name must be at least 3 characters long."
            )

        # SKU logic
        combined_sku = ""
        if sku_prefix and sku_number:
            combined_sku = f"{sku_prefix}-{sku_number}"
        elif sku_prefix:
            combined_sku = sku_prefix
        elif sku_number:
            errors.setdefault("sku_prefix", []).append(
                "SKU Prefix is required if SKU Number is provided."
            )
            errors.setdefault("sku_number", []).append(
                "SKU Prefix is required if SKU Number is provided."
            )
        else:
            # If both are empty, consider SKU as required for editing unless it's explicitly allowed to be empty
            # For now, let's assume SKU is always required.
            errors.setdefault("sku_prefix", []).append("SKU is required.")
            errors.setdefault("sku_number", []).append("SKU is required.")

        if combined_sku:
            # Check for uniqueness, excluding the current item being edited
            existing_items = Item.objects.filter(sku=combined_sku).exclude(pk=item.pk)
            if existing_items.exists():
                errors.setdefault("sku", []).append(  # Use 'sku' for the combined error
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

        # Inventory fields
        opening_stock = None
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

        # --- Handle Errors and Render Form ---
        if errors:
            messages.error(
                request, "Please correct the errors below."
            )  # <--- Consolidated message

            # Recalculate image_exists and current_image_url for form re-population
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
            return render(request, "forms/edit/edit_item.html", context)

        # --- Save if No Errors ---
        try:
            with transaction.atomic():
                item.name = name
                item.sku = combined_sku
                item.unit = selected_unit
                item.category = selected_category
                item.selling_price = selling_price
                item.purchase_price = purchase_price
                item.opening_stock = opening_stock
                item.reorder_point = reorder_point
                item.save()

                # Clear image if requested
                if clear_image_requested and current_item_image:
                    current_item_image.image.delete(save=False)
                    current_item_image.delete()
                    current_item_image = None

                # Upload new image
                if new_image_file:
                    if (
                        current_item_image
                    ):  # Delete existing image if a new one is uploaded
                        current_item_image.image.delete(save=False)
                        current_item_image.delete()
                    ItemImage.objects.create(item=item, image=new_image_file)

            messages.success(request, f'Item "{item.name}" updated successfully!')
            return redirect("view_item", pk=item.pk)

        except IntegrityError:
            # This catches database-level errors, e.g., unique constraint violation for SKU
            errors["sku"] = [
                "An item with this SKU already exists (database conflict)."
            ]
            messages.error(
                request,
                "A database error occurred, possibly a duplicate SKU. Please correct the highlighted field.",
            )
            # Re-render with errors
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
            return render(request, "forms/edit/edit_item.html", context)

        except ValidationError as e:
            all_validation_errors = []
            for field, field_errors in e.message_dict.items():
                errors[field] = errors.get(field, []) + field_errors
                for error_msg in field_errors:
                    all_validation_errors.append(
                        f"{field.replace('_', ' ').title()}: {error_msg}"
                    )

            if all_validation_errors:
                messages.error(
                    request,
                    "Please correct the following issues: "
                    + "; ".join(all_validation_errors),
                )
            else:
                messages.error(request, "Please correct the errors below.")

            # Re-render with errors
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
            return render(request, "forms/edit/edit_item.html", context)

        except Exception:
            messages.error(
                request, "An unexpected server error occurred. Please try again."
            )
            import traceback

            traceback.print_exc()

            # Re-render with errors
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
                "errors": {"general": ["An unexpected error occurred."]},
                "units": UnitOfMeasure.objects.all(),
                "categories": Category.objects.all(),
                "current_image_url": current_image_url,
                "image_exists": image_exists,
            }
            return render(request, "forms/edit/edit_item.html", context)

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

    return render(request, "forms/edit/edit_item.html", context)


@login_required
def view_item(request, pk):
    item = get_object_or_404(Item, pk=pk)
    sales = Sale.objects.filter(item=item).order_by("-date")

    context = {
        "item": item,
        "sales": sales,
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
    return render(request, "forms/import/import_items.html")


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
    """
    View to handle adding a new category using Django forms and Crispy Forms.
    """
    if request.method == "POST":
        # Create a form instance and populate it with data from the request
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Category added successfully.")
            return redirect("categories")
        else:
            # If the form is not valid, the form object itself will contain
            # the submitted data and validation errors
            pass
    else:
        # For GET requests, create a blank form
        form = CategoryForm()

    return render(
        request,
        "forms/add/add_category.html",
        {
            "form": form,
        },
    )


@login_required
def edit_category(request, pk):
    """
    View to handle editing an existing category using Django forms and Crispy Forms.
    """
    # Retrieve the category object or return a 404 error if not found
    category = get_object_or_404(Category, pk=pk)

    if request.method == "POST":
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, "Category updated successfully.")
            return redirect("view_category", pk=category.pk)
        else:
            # If the form is not valid, the form object itself will contain
            # the submitted data and validation errors
            pass
    else:
        # For GET requests, create a form instance pre-populated with the
        # existing category's data by passing 'instance=category'.
        form = CategoryForm(instance=category)

    return render(
        request,
        "forms/edit/edit_category.html",
        {
            "form": form,
            "category": category,
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
    units = UnitOfMeasure.objects.all().annotate(item_count=Count("items"))
    total_units = units.count()

    return render(
        request,
        "units.html",
        {
            "units": units,
            "total_units": total_units,
        },
    )


@login_required
def add_unit(request):
    """
    View to handle adding a new Unit of Measure using Django forms and Crispy Forms.
    """
    if request.method == "POST":
        # Create a form instance and populate it with data from the request
        form = UnitOfMeasureForm(request.POST)
        if form.is_valid():
            # If the form is valid, save the new unit instance.
            form.save()
            messages.success(request, "Unit added successfully.")
            return redirect("units")  # Redirect to your units list page
        else:
            # If the form is not valid, the form object itself will contain
            # the submitted data and validation errors.
            pass
    else:
        # For GET requests, create a blank form
        form = UnitOfMeasureForm()

    return render(
        request,
        "forms/add/add_unit.html",
        {
            "form": form,
        },
    )


@login_required
def edit_unit(request, pk):
    """
    View to handle editing an existing Unit of Measure using Django forms and Crispy Forms.
    """
    # Retrieve the UnitOfMeasure object or return a 404 error if not found
    unit = get_object_or_404(UnitOfMeasure, pk=pk)

    if request.method == "POST":
        form = UnitOfMeasureForm(request.POST, instance=unit)
        if form.is_valid():
            form.save()
            messages.success(request, "Unit updated successfully.")
            # Redirect to a view that shows the details of the updated unit
            return redirect("view_unit", pk=unit.pk)
        else:
            # If the form is not valid, the form object itself will contain
            # the submitted data and validation errors
            pass
    else:
        # For GET requests, create a form instance pre-populated with the
        # existing unit's data by passing 'instance=unit'.
        form = UnitOfMeasureForm(instance=unit)

    return render(
        request,
        "forms/edit/edit_unit.html",
        {
            "form": form,
            "unit": unit,
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
    if request.method == "POST":
        form = InventoryAdjustmentForm(request.POST)
        if form.is_valid():
            adjustment = form.save(commit=False)
            adjustment.user = request.user
            adjustment.save()
            messages.success(request, "Inventory adjustment recorded successfully.")
            return redirect("inventory_adjustments")
    else:
        form = InventoryAdjustmentForm()

    return render(
        request,
        "forms/add/add_adjustment.html",
        {
            "form": form,
            "items": Item.objects.all(),
            "reason_choices": InventoryAdjustment.REASON_CHOICES,
            "errors": form.errors,
            "form_data": form.data,
        },
    )


def edit_adjustment(request, pk):
    adjustment = get_object_or_404(InventoryAdjustment, pk=pk)

    if request.method == "POST":
        form = InventoryAdjustmentForm(request.POST, instance=adjustment)
        print(adjustment.adjustment_type)
        print(adjustment.reason)

        if form.is_valid():
            form.save()
            messages.success(request, "Inventory adjustment updated successfully.")
            return redirect("view_adjustment", pk=adjustment.pk)
        # If form is invalid, it will fall through to re-render with errors
    else:
        form = InventoryAdjustmentForm(instance=adjustment)

    return render(
        request,
        "forms/edit/edit_adjustment.html",
        {
            "form": form,
            "adjustment": adjustment,
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
