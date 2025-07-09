import csv
import os
import uuid
from datetime import datetime
from decimal import Decimal, InvalidOperation
from io import StringIO

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.db.models import Q  # For OR conditions in lookups


def item_image_upload_path(instance, filename):
    ext = filename.split(".")[-1]
    item_sku = instance.item.sku.replace(" ", "_")
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    unique_id = uuid.uuid4().hex[:6]
    filename = f"{item_sku}_{timestamp}_{unique_id}.{ext}"
    return os.path.join("item_images", item_sku, filename)


def generate_item_csv_template():
    """
    Generates a CSV template for the Item model with predefined columns.

    Returns:
        StringIO: A StringIO object containing the CSV data.
    """
    # Define the column headers for the CSV template.
    # These should correspond to the fields in your Item model that you want
    # users to be able to import or update.
    # For ForeignKey fields (unit, category), we'll use their 'name' or 'abbreviation'.
    field_names = [
        "name",
        "sku",
        "unit",  # Expects UnitOfMeasure.name or abbreviation
        "category",  # Expects Category.name
        "selling_price",
        "purchase_price",
        "opening_stock",
        "reorder_point",
        "current_stock",
    ]

    # Create an in-memory text buffer
    output = StringIO()
    writer = csv.writer(output)

    # Write the header row
    writer.writerow(field_names)

    # Optionally, write a sample row to guide the user
    # This sample data should be illustrative of the expected format
    sample_data = [
        "Sample Item A",
        "SKU-001",
        "Pieces",  # Example UnitOfMeasure name
        "Electronics",  # Example Category name
        "100.50",
        "75.25",
        "100",
        "20",
        "100",
    ]
    writer.writerow(sample_data)

    # Reset the buffer's position to the beginning so that its content can be read
    output.seek(0)
    return output


def process_item_csv_upload(csv_file):
    """
    Processes an uploaded CSV file to import or update Item records.
    Automatically creates UnitOfMeasure and Category objects if they do not exist.

    Args:
        csv_file: A Django UploadedFile object.

    Returns:
        dict: A dictionary containing import statistics and detailed errors.
              Example: {
                  'total_rows': 10,
                  'successful_imports': 8,
                  'failed_imports': 2,
                  'errors': [
                      {'row_num': 3, 'data': {'name': 'Bad Item'}, 'messages': ['SKU is required.']},
                      {'row_num': 5, 'data': {'name': 'Another Item'}, 'messages': ['Invalid selling price.']},
                  ]
              }
    """
    # Moved imports inside the function to avoid circular dependency
    from .models import Category, Item, UnitOfMeasure

    decoded_file = csv_file.read().decode("utf-8")
    io_string = StringIO(decoded_file)
    reader = csv.reader(io_string)

    headers = []
    data_rows = []

    # Read headers and data rows
    try:
        headers = [
            h.strip().lower() for h in next(reader)
        ]  # Convert headers to lowercase for flexible matching
        for row in reader:
            data_rows.append(row)
    except StopIteration:
        return {
            "total_rows": 0,
            "successful_imports": 0,
            "failed_imports": 0,
            "errors": [
                {"row_num": 0, "data": {}, "messages": ["The CSV file is empty."]}
            ],
        }
    except Exception as e:
        return {
            "total_rows": 0,
            "successful_imports": 0,
            "failed_imports": 0,
            "errors": [
                {
                    "row_num": 0,
                    "data": {},
                    "messages": [f"Error reading CSV headers: {e}"],
                }
            ],
        }

    # Expected column names from the template
    expected_headers = [
        "name",
        "sku",
        "unit",
        "category",
        "selling_price",
        "purchase_price",
        "opening_stock",
        "reorder_point",
        "current_stock",
    ]

    # Validate headers
    if not all(header in headers for header in expected_headers):
        missing_headers = [h for h in expected_headers if h not in headers]
        return {
            "total_rows": len(data_rows),
            "successful_imports": 0,
            "failed_imports": len(data_rows),
            "errors": [
                {
                    "row_num": 0,
                    "data": {},
                    "messages": [
                        f'CSV headers do not match the template. Missing: {", ".join(missing_headers)}'
                    ],
                }
            ],
        }

    # Create a mapping from header name to column index
    header_to_index = {header: headers.index(header) for header in expected_headers}

    successful_imports = 0
    failed_imports = 0
    errors = []

    for i, row in enumerate(data_rows):
        row_num = i + 2  # +1 for 0-indexed list, +1 for header row
        row_data = {}
        row_errors = []

        # Populate row_data based on header mapping
        for field_name in expected_headers:
            col_index = header_to_index[field_name]
            # Ensure row has enough columns
            if col_index < len(row):
                row_data[field_name] = row[col_index].strip()
            else:
                row_data[field_name] = ""  # Default to empty string if column missing

        # --- Data Cleaning and Validation for each row ---
        name = row_data.get("name")
        sku = row_data.get("sku")
        unit_value = row_data.get("unit")  # Renamed to avoid conflict with unit_obj
        category_name = row_data.get("category")
        selling_price_str = row_data.get("selling_price")
        purchase_price_str = row_data.get("purchase_price")
        opening_stock_str = row_data.get("opening_stock")
        reorder_point_str = row_data.get("reorder_point")
        current_stock_str = row_data.get("current_stock")

        # 1. Name
        if not name:
            row_errors.append("Name is required.")

        # 2. SKU
        if not sku:
            row_errors.append("SKU is required.")

        # 3. UnitOfMeasure Lookup and Creation (UPDATED FOR OPTIONAL ABBREVIATION)
        unit_obj = None
        if not unit_value:
            row_errors.append("Unit of Measure is required.")
        else:
            try:
                # First, try to get the existing unit using the Q object
                unit_obj = UnitOfMeasure.objects.get(
                    Q(name__iexact=unit_value) | Q(abbreviation__iexact=unit_value)
                )
            except UnitOfMeasure.DoesNotExist:
                # If not found, create a new one, setting only the name
                # Abbreviation will be left blank, which requires blank=True in the model
                try:
                    unit_obj = UnitOfMeasure.objects.create(
                        name=unit_value, abbreviation=""
                    )  # Explicitly set to empty string
                    # Optionally, add a message about new unit creation if desired for detailed logs
                except IntegrityError:
                    row_errors.append(
                        f"Could not create Unit of Measure '{unit_value}'. A unit with this name or abbreviation might already exist."
                    )
                except (
                    ValidationError
                ) as e:  # Catch model validation errors during creation
                    for field, field_errors in e.message_dict.items():
                        row_errors.append(
                            f"UnitOfMeasure {field.replace('_', ' ').title()}: {'; '.join(field_errors)}"
                        )
                except Exception as e:
                    row_errors.append(
                        f"Error creating Unit of Measure '{unit_value}': {e}"
                    )
            except UnitOfMeasure.MultipleObjectsReturned:
                row_errors.append(
                    f"Multiple Units of Measure found for '{unit_value}'. Please ensure unit names/abbreviations are unique in your system or use a more specific value in the CSV (e.g., abbreviation)."
                )
            except Exception as e:
                row_errors.append(
                    f"Error processing Unit of Measure '{unit_value}': {e}"
                )

        # 4. Category Lookup and Creation
        category_obj = None
        if category_name:
            try:
                # Automatically create category if it doesn't exist
                category_obj, created = Category.objects.get_or_create(
                    name__iexact=category_name,  # Case-insensitive lookup
                    defaults={
                        "name": category_name
                    },  # Use the provided name for creation
                )
                if created:
                    # You might want to log this or add a message, but not an error
                    pass
            except Exception as e:
                row_errors.append(f"Error processing Category '{category_name}': {e}")

        # 5. Selling Price
        selling_price = None
        if selling_price_str:
            try:
                selling_price = Decimal(selling_price_str)
                if selling_price < 0:
                    row_errors.append("Selling price cannot be negative.")
            except InvalidOperation:
                row_errors.append("Invalid selling price format.")

        # 6. Purchase Price
        purchase_price = None
        if purchase_price_str:
            try:
                purchase_price = Decimal(purchase_price_str)
                if purchase_price < 0:
                    row_errors.append("Purchase price cannot be negative.")
            except InvalidOperation:
                row_errors.append("Invalid purchase price format.")

        # 7. Inventory fields (can be null/blank in model, but validate format if provided)
        opening_stock = None
        if opening_stock_str:
            try:
                opening_stock = int(opening_stock_str)
                if opening_stock < 0:
                    row_errors.append("Opening stock cannot be negative.")
            except ValueError:
                row_errors.append(
                    "Invalid opening stock format (must be a whole number)."
                )

        reorder_point = None
        if reorder_point_str:
            try:
                reorder_point = int(reorder_point_str)
                if reorder_point < 0:
                    row_errors.append("Reorder point cannot be negative.")
            except ValueError:
                row_errors.append(
                    "Invalid reorder point format (must be a whole number)."
                )

        current_stock = 0  # Default to 0 as per model
        if current_stock_str:
            try:
                current_stock = int(current_stock_str)
                if current_stock < 0:
                    row_errors.append("Current stock cannot be negative.")
            except ValueError:
                row_errors.append(
                    "Invalid current stock format (must be a whole number)."
                )

        # If there are no row-specific validation errors, attempt to save/update
        if not row_errors:
            try:
                with transaction.atomic():
                    item_instance, created = Item.objects.get_or_create(
                        sku=sku,  # Use SKU for lookup
                        defaults={
                            "name": name,
                            "unit": unit_obj,
                            "category": category_obj,
                            "selling_price": selling_price,
                            "purchase_price": purchase_price,
                            "opening_stock": opening_stock,
                            "reorder_point": reorder_point,
                            "current_stock": current_stock,
                        },
                    )
                    if not created:
                        # Update existing item
                        item_instance.name = name
                        item_instance.unit = unit_obj
                        item_instance.category = category_obj
                        item_instance.selling_price = selling_price
                        item_instance.purchase_price = purchase_price
                        item_instance.opening_stock = opening_stock
                        item_instance.reorder_point = reorder_point
                        item_instance.current_stock = (
                            current_stock  # Update current stock directly
                        )

                    # Call full_clean for model-level validation before saving
                    item_instance.full_clean()
                    item_instance.save()
                    successful_imports += 1

            except IntegrityError:
                row_errors.append(
                    f"SKU '{sku}' already exists. Item not imported/updated to avoid duplication."
                )
            except ValidationError as e:
                # Catch model-level validation errors
                for field, field_errors in e.message_dict.items():
                    row_errors.append(
                        f"{field.replace('_', ' ').title()}: {'; '.join(field_errors)}"
                    )
            except Exception as e:
                row_errors.append(f"An unexpected error occurred: {e}")

        if row_errors:
            failed_imports += 1
            errors.append(
                {"row_num": row_num, "data": row_data, "messages": row_errors}
            )

    return {
        "total_rows": len(data_rows),
        "successful_imports": successful_imports,
        "failed_imports": failed_imports,
        "errors": errors,
    }
