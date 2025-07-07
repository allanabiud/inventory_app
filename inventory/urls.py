from django.urls import path

from . import views

urlpatterns = [
    path("inventory/items/", views.items_view, name="items"),
    path("inventory/items/import/", views.import_items_view, name="import_items"),
    path(
        "inventory/items/download-template/",
        views.download_item_csv_template_view,
        name="download_item_csv_template",
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
]
