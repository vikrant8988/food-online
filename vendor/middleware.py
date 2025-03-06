from django.shortcuts import redirect
from django.urls import reverse
from django.core.exceptions import PermissionDenied
from accounts.models import User

class LoginRequiredMiddleware:
    """Middleware to enforce login and vendor role for vendor URLs."""
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/accounts/vendor/'):
            # If user is not authenticated, redirect to login
            if not request.user.is_authenticated:
                raise PermissionDenied

            # If user is authenticated but not a vendor, deny access
            if not hasattr(request.user, 'role') or request.user.role != User.VENDOR:
                raise PermissionDenied
        
        return self.get_response(request)
