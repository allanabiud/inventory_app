from django.urls import path

from . import views

urlpatterns = [
    path("items/", views.items_view, name="items"),
]
