from django.urls import path

from . import views

urlpatterns = [
    path("purchases", views.purchases_view, name="purchases"),
    path("purchases/add-purchase/", views.add_purchase, name="add_purchase"),
    path(
        "purchases/view-purchase/<int:pk>/", views.view_purchase, name="view_purchase"
    ),
    path(
        "purchases/edit-purchase/<int:pk>/", views.edit_purchase, name="edit_purchase"
    ),
    path(
        "purchases/delete-purchase/<int:pk>/",
        views.delete_purchase,
        name="delete_purchase",
    ),
    path(
        "purchases/delete-all-purchases/",
        views.delete_all_purchases,
        name="delete_all_purchases",
    ),
    path("purchases/suppliers/", views.supplier_view, name="suppliers"),
    path("suppliers/<int:pk>/", views.view_supplier, name="view_supplier"),
    path("suppliers/add/", views.add_supplier, name="add_supplier"),
    path("suppliers/<int:pk>/edit/", views.edit_supplier, name="edit_supplier"),
    path("suppliers/<int:pk>/delete/", views.delete_supplier, name="delete_supplier"),
    path(
        "suppliers/delete-all-suppliers/",
        views.delete_all_suppliers,
        name="delete_all_suppliers",
    ),
]
