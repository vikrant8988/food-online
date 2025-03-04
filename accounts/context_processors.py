from vendor.models import Vendor

def get_vendor(request):
    if request.user.is_authenticated:
        try:
            vendor = Vendor.objects.get(user=request.user)
            return {'vendor': vendor}
        except Vendor.DoesNotExist:
            return {'vendor': None}  # Handle cases where the user is not a vendor
    return {}  # Return an empty dictionary if the user is not authenticated
