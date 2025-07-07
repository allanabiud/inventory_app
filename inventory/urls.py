from django.urls import path

from . import views

urlpatterns = [
    path("inventory/items/", views.items_view, name="items"),
    path("inventory/items/add-item/", views.add_item, name="add_item"),
]
