from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import CreateView
from django.urls import reverse_lazy

from .forms import RegisterForm, LoginForm, ProfileUpdateForm


def register_view(request):
    """Handle user registration."""
    if request.user.is_authenticated:
        return redirect('dashboard:home')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome to SafeZone AI, {user.first_name}! 🎉")
            return redirect('dashboard:home')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = RegisterForm()

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    """Handle user login."""
    if request.user.is_authenticated:
        return redirect('dashboard:home')

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.first_name or user.username}!")
            # Redirect admin to admin panel
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            if user.is_staff or (hasattr(user, 'profile') and user.profile.is_admin):
                return redirect('admin_panel:dashboard')
            return redirect('dashboard:home')
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = LoginForm(request)

    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    """Logout and redirect to landing page."""
    logout(request)
    messages.info(request, "You have been logged out successfully.")
    return redirect('crime:landing')


@login_required
def profile_view(request):
    """View and update user profile."""
    profile = request.user.profile

    if request.method == 'POST':
        form = ProfileUpdateForm(
            request.POST,
            request.FILES,
            instance=profile,
            user=request.user
        )
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('accounts:profile')
        else:
            messages.error(request, "Please correct the errors.")
    else:
        form = ProfileUpdateForm(instance=profile, user=request.user)

    return render(request, 'accounts/profile.html', {
        'form': form,
        'profile': profile
    })
