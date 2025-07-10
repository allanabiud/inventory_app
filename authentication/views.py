from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseForbidden
from django.shortcuts import redirect, render
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

from .forms import CustomAuthenticationForm, CustomUserCreationForm
from .models import InvitedUser, UserProfile


def root_view(request):
    if request.user.is_authenticated:
        return redirect("home")
    else:
        return redirect("signin")


def signin_view(request):
    if request.user.is_authenticated:
        return redirect("home")
    form = CustomAuthenticationForm(request, data=request.POST or None)

    if form.is_valid():
        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password")
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "Signed in.")
            return redirect("home")
        else:
            messages.error(request, "Invalid login credentials.")
    else:
        if request.method == "POST":
            for error in form.non_field_errors():
                messages.error(request, "Invalid login credentials.")

    return render(request, "signin.html", {"form": form})


def signout_view(request):
    logout(request)
    messages.success(request, "Signed out.")
    return redirect("signin")


def signup(request, token):
    s = URLSafeTimedSerializer(settings.SECRET_KEY)

    try:
        email = s.loads(token, salt="invitation", max_age=60 * 60 * 24)  # 24h expiry
        invited_user = InvitedUser.objects.get(email=email, accepted=False)
    except (BadSignature, SignatureExpired, InvitedUser.DoesNotExist):
        return HttpResponseForbidden("Invalid or expired invitation.")

    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.email = invited_user.email
            user.save()

            # Create user profile
            UserProfile.objects.create(user=user)

            # Link invited user
            invited_user.user = user
            invited_user.accepted = True
            invited_user.save()

            messages.success(
                request, "Account created successfully. You can now sign in."
            )
            return redirect("signin")
        else:
            for error in form.non_field_errors():
                messages.error(request, f"{error}")
    else:
        form = CustomUserCreationForm(initial={"email": email})

    return render(request, "signup.html", {"form": form})
