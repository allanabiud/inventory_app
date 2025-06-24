from django.urls import path

from . import views

urlpatterns = [
    path("", views.root_view, name="signin"),
    path("signin/", views.signin_view, name="signin"),
    path("signout/", views.signout_view, name="signout"),
    path("signup/<token>/", views.signup, name="signup"),
]
