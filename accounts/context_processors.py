from django.conf import settings
from vendor.models import Vendor

def get_vendor(request):
    if request.user.is_authenticated:
        try:
            vendor = Vendor.objects.get(user=request.user)
            return {'vendor': vendor}
        except Vendor.DoesNotExist:
            return {'vendor': None}  # Handle cases where the user is not a vendor
    return {}  # Return an empty dictionary if the user is not authenticated


def get_paypal_client_id(request):
    return {'PAYPAL_CLIENT_ID':settings.PAYPAL_CLIENT_ID}
