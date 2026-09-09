from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views import View
from .forms import LoginForm, PatientRegistrationForm, UserProfileForm
from .models import UserProfile


class LoginView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('accounts:dashboard')
        return render(request, 'accounts/login.html', {'form': LoginForm()})

    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            login(request, form.user)
            messages.success(request, f"Welcome back, {form.user.get_full_name()}!")
            next_url = request.GET.get('next', 'accounts:dashboard')
            return redirect(next_url)
        return render(request, 'accounts/login.html', {'form': form})


class LogoutView(View):
    def post(self, request):
        logout(request)
        messages.info(request, "You have been securely logged out.")
        return redirect('accounts:login')

    def get(self, request):
        logout(request)
        return redirect('accounts:login')


class PatientRegisterView(View):
    def get(self, request):
        return render(request, 'accounts/register.html', {'form': PatientRegistrationForm()})

    def post(self, request):
        form = PatientRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Your patient account has been created successfully.")
            return redirect('accounts:dashboard')
        return render(request, 'accounts/register.html', {'form': form})


@login_required
def dashboard_view(request):
    return render(request, 'accounts/dashboard.html', {'user': request.user})


@login_required
def profile_view(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated.")
            return redirect('accounts:profile')
    else:
        form = UserProfileForm(instance=profile)
    return render(request, 'accounts/profile.html', {'form': form, 'profile': profile})
