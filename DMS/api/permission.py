# permissions.py

from rest_framework import permissions
from rest_framework.permissions import BasePermission

class IsSuperAdminOrOwnClient(permissions.BasePermission):
    """
    Allows access to DashboardUser (superadmin) for all clients,
    and to ClientUser only for their own client data.
    """
    def has_object_permission(self, request, view, obj):
        user = request.user

        # Dashboard user can access any client
        if user.role == 'superuser':
            return True

        # Client user can only access their own client
        if user.role == 'clientuser':
            # If the object itself is a Client instance
            if isinstance(obj, Client):
                return obj == user.client

            # If the object has a client foreign key
            elif hasattr(obj, 'client'):
                return obj.client == user.client

        # All other roles — no access
        return False

class IsSuperUser(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'superuser'


class IsClientUser(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'clientuser'


class IsCustomerUser(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'customeruser'

class IsSuperUserOrClientUser(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            (request.user.role == "superuser" or request.user.role == "clientuser")
        )
