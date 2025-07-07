import csv
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from .models import Category, Item, ItemImage, UnitOfMeasure


@login_required
def items_view(request):
    """
    Displays a list of all items.
    Requires user to be logged in.
    """
    items = Item.objects.all()
    context = {"items": items}
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
        sku_prefix = request.POST.get("sku_prefix", "").strip()
        sku_number = request.POST.get("sku_number", "").strip()
        sku = request.POST.get("sku", "").strip()  # Combined SKU from JS

        unit_id = request.POST.get("unit")
        category_id = request.POST.get("category")
        selling_price_str = request.POST.get("selling_price")
        purchase_price_str = request.POST.get("purchase_price")

        track_inventory = request.POST.get("track_inventory") == "on"
        opening_stock_str = request.POST.get("opening_stock")
        current_stock_str = request.POST.get("current_stock")
        reorder_point_str = request.POST.get("reorder_point")

        image_file = request.FILES.get("image")

        # Store submitted data to re-populate the form in case of errors
        form_data = {
            "name": name,
            "sku_prefix": sku_prefix,
            "sku_number": sku_number,
            "sku": sku,
            "unit": unit_id,
            "category": category_id,
            "selling_price": selling_price_str,
            "purchase_price": purchase_price_str,
            "track_inventory": track_inventory,
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
        if not sku:
            errors["sku"] = ["SKU (Prefix and/or Number) is required."]
        if not unit_id:
            errors["unit"] = ["Unit of Measure is required."]

        if "sku" not in errors and sku and Item.objects.filter(sku=sku).exists():
            errors["sku"] = ["An item with this SKU already exists."]

        if unit_id:
            try:
                validated_unit = UnitOfMeasure.objects.get(pk=unit_id)
            except UnitOfMeasure.DoesNotExist:
                errors["unit"] = ["Invalid Unit of Measure selected."]

        if category_id:
            try:
                validated_category = Category.objects.get(pk=category_id)
            except Category.DoesNotExist:
                errors["category"] = ["Invalid Category selected."]

        try:
            if selling_price_str:
                validated_selling_price = Decimal(selling_price_str)
        except (ValueError, Decimal.InvalidOperation):
            errors["selling_price"] = ["Please enter a valid selling price."]

        try:
            if purchase_price_str:
                validated_purchase_price = Decimal(purchase_price_str)
        except (ValueError, Decimal.InvalidOperation):
            errors["purchase_price"] = ["Please enter a valid purchase price."]

        if track_inventory:
            try:
                if not opening_stock_str:
                    errors["opening_stock"] = [
                        "Opening Stock is required when tracking inventory."
                    ]
                else:
                    validated_opening_stock = int(opening_stock_str)
            except ValueError:
                errors["opening_stock"] = [
                    "Please enter a valid number for Opening Stock."
                ]

            if current_stock_str:
                try:
                    validated_current_stock = int(current_stock_str)
                except ValueError:
                    errors["current_stock"] = [
                        "Please enter a valid number for Current Stock."
                    ]
            elif validated_opening_stock is not None:
                validated_current_stock = validated_opening_stock
            else:
                validated_current_stock = 0

            try:
                if not reorder_point_str:
                    errors["reorder_point"] = [
                        "Reorder Point is required when tracking inventory."
                    ]
                else:
                    validated_reorder_point = int(reorder_point_str)
            except ValueError:
                errors["reorder_point"] = [
                    "Please enter a valid number for Reorder Point."
                ]
        else:
            validated_opening_stock = None
            validated_current_stock = 0
            validated_reorder_point = None

        if errors:
            for field, error_list in errors.items():
                for error_msg in error_list:
                    messages.error(
                        request, f"{field.replace('_', ' ').title()}: {error_msg}"
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

        # 3. Create and Save Item if no errors
        try:
            item = Item(
                name=name,
                sku=sku,
                unit=validated_unit,
                category=validated_category,
                selling_price=validated_selling_price,
                purchase_price=validated_purchase_price,
                track_inventory=track_inventory,
                opening_stock=validated_opening_stock,
                current_stock=validated_current_stock,
                reorder_point=validated_reorder_point,
            )
            item.full_clean()  # Perform model-level validation
            item.save()

            if image_file:
                ItemImage.objects.create(item=item, image=image_file)

            messages.success(request, f'Item "{item.name}" added successfully!')
            return redirect("items")

        except IntegrityError:
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
                "errors": {
                    "sku": ["A database error occurred, possibly a duplicate SKU."]
                },
            }
            return render(request, "forms/add_item.html", context)

        except ValidationError as e:
            for field, field_errors in e.message_dict.items():
                for error_msg in field_errors:
                    messages.error(
                        request, f"{field.replace('_', ' ').title()}: {error_msg}"
                    )
                    errors[field] = errors.get(field, []) + [error_msg]

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
            messages.error(request, f"An unexpected error occurred: {e}")
            units = UnitOfMeasure.objects.all()
            categories = Category.objects.all()
            context = {
                "units": units,
                "categories": categories,
                "form_data": form_data,
                "errors": {"general": [f"An unexpected error occurred: {e}"]},
            }
            return render(request, "forms/add_item.html", context)

    else:  # GET request
        form_data = {
            "name": "",
            "sku_prefix": "SKU",
            "sku_number": "",
            "sku": "",
            "unit": "",
            "category": "",
            "selling_price": "",
            "purchase_price": "",
            "track_inventory": False,
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
        "errors": errors,
    }
    return render(request, "forms/add_item.html", context)


@login_required
def import_items_view(request):
    """
    Handles the import of items from a CSV file.
    Allows users to upload a CSV with item data, which will either create new
    items or update existing ones based on SKU.
    Requires user to be logged in.
    """
    if request.method == "POST":
        if "csv_file" in request.FILES:
            csv_file = request.FILES["csv_file"]
            if not csv_file.name.endswith(".csv"):
                messages.error(
                    request, "This is not a CSV file. Please upload a .csv file."
                )
                return render(request, "forms/import_form.html", {})

            try:
                decoded_file = csv_file.read().decode("utf-8").splitlines()
                reader = csv.DictReader(decoded_file)

                items_created_count = 0
                items_updated_count = 0
                errors = []

                # --- Expected CSV headers ---
                # name,sku_prefix,sku_number,unit,category,selling_price,purchase_price,track_inventory,opening_stock,current_stock,reorder_point

                for i, row in enumerate(reader):
                    row_num = i + 2  # +1 for 0-index, +1 for header row
                    try:
                        name = row.get("name")
                        sku_prefix = row.get("sku_prefix", "").strip()  # Get prefix
                        sku_number = row.get("sku_number", "").strip()  # Get number

                        # --- NEW LOGIC: Combine SKU prefix and number ---
                        if sku_prefix and sku_number:
                            sku = f"{sku_prefix}-{sku_number}"
                        elif sku_prefix:
                            sku = sku_prefix
                        elif sku_number:
                            sku = sku_number
                        else:
                            sku = None  # Or raise an error if SKU is strictly required
                        # --- END NEW LOGIC ---

                        unit_name = row.get(
                            "unit"
                        )  # Changed from "unit_name" to "unit" to match CSV
                        category_name = row.get(
                            "category"
                        )  # Changed from "category_name" to "category" to match CSV
                        selling_price_str = row.get("selling_price")
                        purchase_price_str = row.get("purchase_price")
                        track_inventory_str = row.get(
                            "track_inventory", "FALSE"
                        ).upper()
                        opening_stock_str = row.get("opening_stock")
                        current_stock_str = row.get("current_stock")
                        reorder_point_str = row.get("reorder_point")

                        if not name or not sku or not unit_name:  # Check combined SKU
                            errors.append(
                                f"Row {row_num}: Missing required fields (Name, SKU, Unit). Skipping."
                            )
                            continue

                        # Ensure UnitOfMeasure exists or create it
                        unit, created_unit = UnitOfMeasure.objects.get_or_create(
                            name=unit_name
                        )
                        if created_unit:
                            messages.info(
                                request, f"Created new Unit of Measure: {unit_name}"
                            )

                        # Ensure Category exists or create it (if provided)
                        category = None
                        if category_name:
                            category, created_cat = Category.objects.get_or_create(
                                name=category_name
                            )
                            if created_cat:
                                messages.info(
                                    request, f"Created new Category: {category_name}"
                                )

                        # Convert prices to Decimal
                        selling_price = (
                            Decimal(selling_price_str) if selling_price_str else None
                        )
                        purchase_price = (
                            Decimal(purchase_price_str) if purchase_price_str else None
                        )

                        # Convert track_inventory to boolean
                        track_inventory = track_inventory_str == "TRUE"

                        opening_stock = 0
                        current_stock = 0
                        reorder_point = None

                        if track_inventory:
                            try:
                                opening_stock = (
                                    int(opening_stock_str) if opening_stock_str else 0
                                )
                            except ValueError:
                                errors.append(
                                    f"Row {row_num}: Invalid Opening Stock value '{opening_stock_str}'. Defaulting to 0."
                                )
                                opening_stock = 0

                            try:
                                current_stock = (
                                    int(current_stock_str)
                                    if current_stock_str
                                    else opening_stock  # Default to opening_stock if current_stock is empty
                                )
                            except ValueError:
                                errors.append(
                                    f"Row {row_num}: Invalid Current Stock value '{current_stock_str}'. Defaulting to Opening Stock ({opening_stock})."
                                )
                                current_stock = opening_stock

                            try:
                                reorder_point = (
                                    int(reorder_point_str)
                                    if reorder_point_str
                                    else None
                                )
                            except ValueError:
                                errors.append(
                                    f"Row {row_num}: Invalid Reorder Point value '{reorder_point_str}'. Setting to None."
                                )
                                reorder_point = None
                        else:
                            # If not tracking inventory, these fields should be None or 0 depending on your model definition
                            opening_stock = None  # Or 0, match your Item model's field defaults/nullability
                            current_stock = 0
                            reorder_point = None

                        # Try to get existing item by combined SKU, or create a new one
                        item, created = Item.objects.get_or_create(
                            sku=sku,
                            defaults={
                                "name": name,
                                "unit": unit,
                                "category": category,
                                "selling_price": selling_price,
                                "purchase_price": purchase_price,
                                "track_inventory": track_inventory,
                                "opening_stock": opening_stock,
                                "current_stock": current_stock,
                                "reorder_point": reorder_point,
                            },
                        )

                        if not created:
                            # Update existing item
                            item.name = name
                            item.unit = unit
                            item.category = category
                            item.selling_price = selling_price
                            item.purchase_price = purchase_price
                            item.track_inventory = track_inventory

                            if track_inventory:
                                item.opening_stock = opening_stock
                                item.current_stock = current_stock
                                item.reorder_point = reorder_point
                            else:
                                item.opening_stock = None  # Or 0
                                item.current_stock = 0
                                item.reorder_point = None
                            item.save()
                            items_updated_count += 1
                        else:
                            items_created_count += 1

                    except (
                        ValueError,
                        TypeError,
                        # UnitOfMeasure.DoesNotExist, # .get_or_create handles this
                        # Category.DoesNotExist,      # .get_or_create handles this
                    ) as e:
                        errors.append(
                            f"Row {row_num}: Data conversion error - {e}. Skipping row."
                        )
                    except Exception as e:
                        errors.append(
                            f"Row {row_num}: An unexpected error occurred - {e}. Skipping row."
                        )

                if items_created_count > 0 or items_updated_count > 0:
                    messages.success(
                        request,
                        f"Import complete! Created {items_created_count} items, updated {items_updated_count} items.",
                    )
                if errors:
                    for error_msg in errors:
                        messages.warning(request, error_msg)
                    if not (items_created_count > 0 or items_updated_count > 0):
                        messages.error(
                            request,
                            "No items were imported due to errors. Please check the CSV file.",
                        )

                return redirect(
                    "items"
                )  # Assuming 'items' is the URL name for your item list view

            except Exception as e:
                messages.error(
                    request,
                    f"Error reading CSV file: {e}. Please ensure it is a valid CSV and the headers match.",
                )
                return render(request, "forms/import_form.html", {})
        else:
            messages.error(request, "No CSV file uploaded. Please select a file.")
            return render(request, "forms/import_form.html", {})

    return render(request, "forms/import_form.html", {})


def download_item_csv_template_view(request):
    """
    Generates and downloads a CSV template for item import.
    """
    headers = [
        "name",
        "sku_prefix",
        "sku_number",
        "unit_name",
        "category_name",
        "selling_price",
        "purchase_price",
        "track_inventory",
        "opening_stock",
        "current_stock",
        "reorder_point",
    ]

    example_data = [
        [
            "Example Item 1",
            "SKU",
            "001",
            "Pieces",
            "Electronics",
            "150.00",
            "100.00",
            "TRUE",
            "50",
            "60",
            "10",
        ],
        [
            "Example Item 2",
            "SKU",
            "002",
            "Kilograms",
            "Groceries",
            "5.50",
            "3.00",
            "TRUE",
            "200",
            "120",
            "20",
        ],
    ]

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="item_import_template.csv"'

    writer = csv.writer(response)
    writer.writerow(headers)
    for row in example_data:
        writer.writerow(row)

    return response


def view_item(request, pk):
    item = get_object_or_404(Item, pk=pk)
    context = {
        "item": item,
        # Add any other context data if needed, e.g., form_data for an edit form
    }
    return render(request, "view_item.html", context)


def edit_item(request, pk):
    item = get_object_or_404(Item, pk=pk)

    # Get the current main image instance, if any
    current_item_image = item.images.first()

    # Initialize errors dictionary (will be populated on POST if validation fails)
    errors = {}

    # This dictionary will hold the data to pre-fill the form fields.
    # On GET, it's populated from the existing item.
    # On POST (with errors), it's populated from request.POST.
    form_data = {}

    if request.method == "POST":
        # --- 1. Extract Data from request.POST and request.FILES ---
        name = request.POST.get("name", "").strip()
        sku_prefix = request.POST.get("sku_prefix", "").strip()
        sku_number = request.POST.get("sku_number", "").strip()
        unit_id = request.POST.get("unit")
        category_id = request.POST.get("category")

        selling_price_str = request.POST.get("selling_price", "").strip()
        purchase_price_str = request.POST.get("purchase_price", "").strip()

        track_inventory = request.POST.get("track_inventory") == "on"  # Checkbox value

        opening_stock_str = request.POST.get("opening_stock", "").strip()
        current_stock_str = request.POST.get("current_stock", "").strip()
        reorder_point_str = request.POST.get("reorder_point", "").strip()

        # Image file and clear flag
        new_image_file = request.FILES.get("image")
        clear_image_requested = request.POST.get("clear_image") == "true"

        # Populate form_data with submitted values (for re-rendering if errors)
        form_data = request.POST.copy()
        form_data["track_inventory"] = (
            track_inventory  # Ensure checkbox state is correct
        )

        # --- 2. Perform Manual Validation ---

        # Name
        if not name:
            errors.setdefault("name", []).append("Item name is required.")

        # SKU
        # Combine SKU prefix and number to form the full SKU
        combined_sku = ""
        if sku_prefix and sku_number:
            combined_sku = f"{sku_prefix}-{sku_number}"
        elif sku_prefix:  # If only prefix is provided, use it as full SKU
            combined_sku = sku_prefix
        elif sku_number:
            errors.setdefault("sku_prefix", []).append(
                "SKU Prefix is required if only SKU Number is provided."
            )
            errors.setdefault("sku_number", []).append(
                "SKU Prefix is required if only SKU Number is provided."
            )
        else:  # Both missing
            errors.setdefault("sku_prefix", []).append(
                "SKU Prefix or SKU Number is required."
            )
            errors.setdefault("sku_number", []).append(
                "SKU Prefix or SKU Number is required."
            )

        # Validate unique SKU
        if combined_sku:
            existing_items = Item.objects.filter(sku=combined_sku)
            # Exclude the current item being edited
            existing_items = existing_items.exclude(pk=item.pk)
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
                errors.setdefault("unit", []).append(
                    "Invalid Unit of Measure selected."
                )

        # Category (optional)
        selected_category = None
        if category_id:
            try:
                selected_category = Category.objects.get(pk=category_id)
            except Category.DoesNotExist:
                errors.setdefault("category", []).append("Invalid Category selected.")

        # Selling Price
        selling_price = None
        if selling_price_str:
            try:
                selling_price = Decimal(selling_price_str)
                if selling_price < 0:
                    errors.setdefault("selling_price", []).append(
                        "Selling Price cannot be negative."
                    )
            except InvalidOperation:
                errors.setdefault("selling_price", []).append("Invalid selling price.")
        else:
            # If not explicitly required, but it's often a good idea to have it
            errors.setdefault("selling_price", []).append("Selling Price is required.")

        # Purchase Price
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
                    "Invalid purchase price."
                )
        else:
            errors.setdefault("purchase_price", []).append(
                "Purchase Price is required."
            )

        # Inventory fields (conditional on track_inventory)
        opening_stock = None
        current_stock = None
        reorder_point = None

        if track_inventory:
            # Validate opening_stock
            if not opening_stock_str:
                errors.setdefault("opening_stock", []).append(
                    "Opening Stock is required when tracking inventory."
                )
            else:
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

            # Validate current_stock (often derived or updated separately, but if user can set it directly)
            if not current_stock_str:
                errors.setdefault("current_stock", []).append(
                    "Current Stock is required when tracking inventory."
                )
            else:
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

            # Validate reorder_point
            if not reorder_point_str:
                errors.setdefault("reorder_point", []).append(
                    "Reorder Point is required when tracking inventory."
                )
            else:
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
        else:
            # If not tracking, ensure values are None in the model
            opening_stock = None
            current_stock = None
            reorder_point = None

        # --- 3. Process if no validation errors ---
        if not errors:
            try:
                with transaction.atomic():
                    # Update Item instance fields
                    item.name = name
                    item.sku = combined_sku  # Use the validated, combined SKU
                    item.unit = selected_unit
                    item.category = selected_category
                    item.selling_price = selling_price
                    item.purchase_price = purchase_price
                    item.track_inventory = track_inventory
                    item.opening_stock = opening_stock
                    item.current_stock = current_stock
                    item.reorder_point = reorder_point
                    item.save()  # Save the main item

                    # --- Image Handling Logic ---
                    # 1. Handle clearing the existing image
                    if clear_image_requested:
                        if current_item_image:
                            # Delete the actual image file from storage
                            current_item_image.image.delete(save=False)
                            # Delete the ItemImage model instance from the database
                            current_item_image.delete()
                        current_item_image = None  # Reset for clarity

                    # 2. Handle new image upload
                    if new_image_file:
                        # If there was an old image *and it wasn't just cleared*, delete it
                        # (This `if` block implicitly handles if `current_item_image` became None from clearing)
                        if current_item_image:
                            current_item_image.image.delete(save=False)
                            current_item_image.delete()

                        # Create a new ItemImage instance for the uploaded file, linked to the item
                        ItemImage.objects.create(item=item, image=new_image_file)

                messages.success(request, f'Item "{item.name}" updated successfully!')
                return redirect("view_item", pk=item.pk)

            except Exception as e:
                # Catch any unexpected errors during save/image handling
                messages.error(request, f"An unexpected error occurred: {e}")
                # Log the error for debugging: print(f"Error saving item: {e}")
                # You might want to add a general error to the form_data or errors dict
                errors.setdefault("general", []).append(
                    f"Server error: {e}. Please try again."
                )

        # If there are errors (or an exception occurred), re-render the form with data and errors
        # Determine the current_image_url for re-rendering with errors
        # If a clear was requested, or a new file was uploaded, the preview might change
        # For an error state, it's generally safest to show the *original* image
        # unless a new one was successfully uploaded (which wouldn't happen if form.is_valid() failed).
        current_image_url_for_template = (
            current_item_image.image.url
            if current_item_image and current_item_image.image
            else None
        )
        image_exists_for_template = bool(
            current_item_image and current_item_image.image
        )

        # If clear was requested in this POST, even if other errors, reflect that in template
        if clear_image_requested:
            current_image_url_for_template = None
            image_exists_for_template = False

        context = {
            "item": item,
            "form_data": form_data,  # Contains request.POST values for re-population
            "errors": errors,  # Contains validation errors
            "units": UnitOfMeasure.objects.all(),
            "categories": Category.objects.all(),
            "current_image_url": current_image_url_for_template,
            "image_exists": image_exists_for_template,
        }

    else:  # GET request (initial load of the page)
        # Populate form_data from the existing item instance
        form_data = {
            "name": item.name,
            # Handle SKU split for display
            "sku_prefix": item.sku.split("-", 1)[0] if item.sku else "",
            "sku_number": (
                item.sku.split("-", 1)[1] if item.sku and "-" in item.sku else ""
            ),
            "unit": item.unit.pk if item.unit else "",
            "category": item.category.pk if item.category else "",
            "selling_price": item.selling_price,
            "purchase_price": item.purchase_price,
            "track_inventory": item.track_inventory,
            "opening_stock": item.opening_stock,
            "current_stock": item.current_stock,
            "reorder_point": item.reorder_point,
        }

        # Determine current image URL for display
        current_image_url_for_template = (
            current_item_image.image.url
            if current_item_image and current_item_image.image
            else None
        )
        image_exists_for_template = bool(
            current_item_image and current_item_image.image
        )

        context = {
            "item": item,
            "form_data": form_data,
            "errors": errors,  # Empty on initial GET
            "units": UnitOfMeasure.objects.all(),
            "categories": Category.objects.all(),
            "current_image_url": current_image_url_for_template,
            "image_exists": image_exists_for_template,
        }

    return render(request, "edit_item.html", context)  # Assuming template path


def delete_item(request, pk):
    item = get_object_or_404(Item, pk=pk)
    if request.method == "POST":
        item.delete()
        messages.success(request, f'Item "{item.name}" deleted successfully.')
        return redirect("items")
    return redirect("view_item", pk=pk)  # If not POST, redirect back to item detail
