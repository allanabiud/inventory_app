from django.urls import path

from . import views

urlpatterns = [
    path("sales-report/", views.sales_report_view, name="sales_report"),
    path("purchases-report/", views.purchases_report_view, name="purchases_report"),
    path(
        "profit-loss-report/", views.profit_loss_report_view, name="profit_loss_report"
    ),
]
