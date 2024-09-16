from rest_framework.permissions import BasePermission
from rest_framework import permissions
from rest_framework.response import Response
from autovm.users.models import Customer


class IsNotSuspendedCustomer(BasePermission):
    """
    Permission class that grants access only to customers who are not suspended.
    """

    message = "Suspended account"

    def has_permission(self, request, view):
        user = request.user

        # Ensure the user is authenticated
        if not user.is_authenticated:
            return False

        try:
            customer = user.customer_profile
        except Customer.DoesNotExist:
            return False

        # Check if the customer is suspended
        if customer.suspended and (request.method not in permissions.SAFE_METHODS):
            return False

        return True
