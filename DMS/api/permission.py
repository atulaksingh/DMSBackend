# permissions.py

from rest_framework import permissions

class IsSuperAdminOrOwnClient(permissions.BasePermission):
    """
    Allows access to DashboardUser (superadmin) for all clients,
    and to ClientUser only for their own client data.
    """
    # def has_object_permission(self, request, view, obj):
    #     user = request.user

    #     if hasattr(user, 'dashboarduser'):
    #         # It's a superadmin user
    #         return user.dashboarduser.superadmin_user is True

    #     elif hasattr(user, 'clientuser'):
    #         # It's a client user - only allow access to their own client
    #         return obj == user.clientuser.client
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

