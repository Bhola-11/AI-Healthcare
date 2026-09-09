from rest_framework import permissions
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
