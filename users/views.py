from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.urls import reverse

from .forms import CustomUserCreationForm


class CustomLoginView(LoginView):
    template_name = "users/login.html"


def register(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get("username")

            messages.success(
                request,
                f'Account created for {username}! You can now log in.'
            )
            return redirect("users:login")
    else:
        form = CustomUserCreationForm()

    return render(request, "users/register.html", {"form": form})