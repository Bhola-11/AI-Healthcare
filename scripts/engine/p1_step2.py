from builder_core import run_cmd, write_file, pr_branch, pr_commit, pr_merge

pr_branch("pr/003-rbac")

perms_code = """from rest_framework import permissions
from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import PermissionDenied


class BaseRolePermission(permissions.BasePermission):
    allowed_roles = []

    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            (request.user.is_superuser or request.user.role in self.allowed_roles)
        )


class IsDoctor(BaseRolePermission):
    allowed_roles = ["DOCTOR", "ADMIN"]


class IsNurse(BaseRolePermission):
    allowed_roles = ["NURSE", "DOCTOR", "ADMIN"]


class IsPatient(BaseRolePermission):
    allowed_roles = ["PATIENT", "ADMIN"]


class IsPharmacist(BaseRolePermission):
    allowed_roles = ["PHARMACIST", "ADMIN"]


class IsLabTech(BaseRolePermission):
    allowed_roles = ["LAB_TECH", "ADMIN"]


class IsBiller(BaseRolePermission):
    allowed_roles = ["BILLER", "ADMIN"]


class IsReceptionist(BaseRolePermission):
    allowed_roles = ["RECEPTIONIST", "ADMIN"]


class RoleRequiredMixin(UserPassesTestMixin):
    allowed_roles = []

    def test_func(self):
        if not self.request.user.is_authenticated:
            return False
        if self.request.user.is_superuser:
            return True
        return self.request.user.role in self.allowed_roles

    def handle_no_permission(self):
        raise PermissionDenied("You do not have clinical or administrative clearance to access this module.")
"""
write_file("apps/accounts/permissions.py", perms_code)

forms_code = """from django import forms
from django.contrib.auth import authenticate
from .models import User, UserProfile


class LoginForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'name@hospital.com'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': '••••••••'}))

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')
        if email and password:
            user = authenticate(email=email, password=password)
            if not user:
                raise forms.ValidationError("Invalid email or password credentials.")
            if not user.is_active:
                raise forms.ValidationError("This healthcare account has been deactivated.")
            self.user = user
        return cleaned_data


class PatientRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-input'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-input'}))

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone_number']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-input'}),
            'last_name': forms.TextInput(attrs={'class': 'form-input'}),
            'email': forms.EmailInput(attrs={'class': 'form-input'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-input'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('password')
        p2 = cleaned_data.get('confirm_password')
        if p1 and p2 and p1 != p2:
            self.add_error('confirm_password', "Passwords do not match.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = User.Role.PATIENT
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
            UserProfile.objects.create(user=user)
        return user


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['date_of_birth', 'gender', 'national_id', 'address_line_1', 'city', 'state', 'postal_code', 'country', 'bio']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'national_id': forms.TextInput(attrs={'class': 'form-input'}),
            'address_line_1': forms.TextInput(attrs={'class': 'form-input'}),
            'city': forms.TextInput(attrs={'class': 'form-input'}),
            'state': forms.TextInput(attrs={'class': 'form-input'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-input'}),
            'country': forms.TextInput(attrs={'class': 'form-input'}),
            'bio': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 3}),
        }
"""
write_file("apps/accounts/forms.py", forms_code)

views_code = """from django.shortcuts import render, redirect
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
"""
write_file("apps/accounts/views.py", views_code)

urls_code = """from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('register/', views.PatientRegisterView.as_view(), name='register'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('profile/', views.profile_view, name='profile'),
]
"""
write_file("apps/accounts/urls.py", urls_code)

pr_commit(["apps/accounts/permissions.py"], "feat(accounts): implement rbac permissions, group fixtures and access policies")
pr_commit(["apps/accounts/forms.py", "apps/accounts/views.py", "apps/accounts/urls.py"], "feat(accounts): implement user registration, login, logout and session management views")
pr_merge("pr/003-rbac")
print("PR 3 merged successfully.")
