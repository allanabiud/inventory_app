from django.urls import path

from . import views

urlpatterns = [
    # Items
    path("inventory/items/", views.items_view, name="items"),
    path("inventory/items/import/", views.import_items_view, name="import_items"),
    path(
        "inventory/items/download-template/",
        views.generate_csv_template_view,
        name="generate_item_csv_template",
    ),
    path("inventory/items/add-item/", views.add_item, name="add_item"),
    path("inventory/items/item/<int:pk>/", views.view_item, name="view_item"),
    path(
        "inventory/items/item/<int:pk>/edit/",
        views.edit_item,
        name="edit_item",
    ),
    path(
        "inventory/items/item/<int:pk>/delete/",
        views.delete_item,
        name="delete_item",
    ),
    path(
        "inventory/items/delete-all/", views.delete_all_items, name="delete_all_items"
    ),
    # Categories
    path("inventory/categories/", views.categories_view, name="categories"),
    path("inventory/categories/add-category/", views.add_category, name="add_category"),
    path("inventory/categories/<int:pk>/", views.view_category, name="view_category"),
    path(
        "inventory/categories/<int:pk>/edit/",
        views.edit_category,
        name="edit_category",
    ),
    path(
        "inventory/categories/<int:pk>/delete/",
        views.delete_category,
        name="delete_category",
    ),
    path(
        "inventory/categories/delete-all/",
        views.delete_all_categories,
        name="delete_all_categories",
    ),
    # Units
    path("inventory/units/", views.units_view, name="units"),
    path("inventory/units/add-unit/", views.add_unit, name="add_unit"),
    path("inventory/units/<int:pk>/edit/", views.edit_unit, name="edit_unit"),
    path("inventory/units/<int:pk>/", views.view_unit, name="view_unit"),
    path("inventory/units/<int:pk>/delete/", views.delete_unit, name="delete_unit"),
    path(
        "inventory/units/delete-all/", views.delete_all_units, name="delete_all_units"
    ),
    # Inventory Adjustments
    path(
        "inventory/adjustments/",
        views.inventory_adjustments,
        name="inventory_adjustments",
    ),
    path(
        "inventory/adjustments/add-adjustment/",
        views.add_adjustment,
        name="add_adjustment",
    ),
    path(
        "inventory/adjustments/<int:pk>/",
        views.view_adjustment,
        name="view_adjustment",
    ),
    path(
        "inventory/adjustments/<int:pk>/edit/",
        views.edit_adjustment,
        name="edit_adjustment",
    ),
    path(
        "inventory/adjustments/<int:pk>/delete/",
        views.delete_adjustment,
        name="delete_adjustment",
    ),
    path(
        "inventory/adjustments/delete-all/",
        views.delete_all_adjustments,
        name="delete_all_adjustments",
    ),
    # Stock Alerts
    path("inventory/stock-alerts/", views.low_stock_view, name="stock_alerts"),
    path(
        "tasks/send-low-stock-email/",
        views.trigger_low_stock_email,
        name="send_low_stock_email",
    ),
]
