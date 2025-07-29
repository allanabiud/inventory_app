from django.urls import path

from . import views

urlpatterns = [
    path("sales/sales-records/", views.sales_view, name="sales"),
    path("sales/add-sale/", views.add_sale, name="add_sale"),
    path("sales/view-sale/<int:pk>/", views.view_sale, name="view_sale"),
    path("sales/edit-sale/<int:pk>/", views.edit_sale, name="edit_sale"),
    path("sales/delete-sale/<int:pk>/", views.delete_sale, name="delete_sale"),
    path("sales/delete-all-sales/", views.delete_all_sales, name="delete_all_sales"),
    path("sales/customers/", views.customers_view, name="customers"),
    path("sales/add-customer/", views.add_customer, name="add_customer"),
    path("sales/edit-customer/<int:pk>/", views.edit_customer, name="edit_customer"),
    path("sales/view-customer/<int:pk>/", views.view_customer, name="view_customer"),
    path(
        "sales/delete-customer/<int:pk>/", views.delete_customer, name="delete_customer"
    ),
    path(
        "sales/delete-all-customers/",
        views.delete_all_customers,
        name="delete_all_customers",
    ),
]
