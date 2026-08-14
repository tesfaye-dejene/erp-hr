from rest_framework.permissions import BasePermission


class IsHRStaff(BasePermission):
    """
    Simple permission placeholder.
    Currently allows anyone (for easy local testing).
    Replace with real role / permission checks in production.
    """

    def has_permission(self, request, view):
        # Open for local testing. Change to require authentication later.
        return True
        # Production example:
        # if not request.user or not request.user.is_authenticated:
        #     return False
        # return request.user.has_perm("hr.view_employee")
