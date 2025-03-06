from django.shortcuts import redirect, render, get_object_or_404

from .forms import VendorForm
from accounts.forms import UserProfileForm
from .models import Vendor
from accounts.models import UserProfile
from django.contrib import messages

def v_profile(request):
  profile = get_object_or_404(UserProfile, user=request.user)
  vendor = get_object_or_404(Vendor, user=request.user)
  
  if request.method == 'POST':
    profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)
    vendor_form = VendorForm(request.POST, request.FILES, instance=vendor)
    
    if profile_form.is_valid() and vendor_form.is_valid():
      profile_form.save()
      vendor_form.save()
      messages.success(request, "Profile updated successfully.")
      return redirect("v_profile")  # ✅ Redirect after form submission
    else:
      print(vendor_form.errors)
      print(profile_form.errors)
      messages.error(request, "Oops! Something went wrong. Please try again later.")
  else:
    profile_form = UserProfileForm(instance=profile)
    vendor_form = VendorForm(instance=vendor)
    
  context= {
    'profile_form': profile_form,
    'vendor_form': vendor_form,
    'vendor' : vendor,
    'profile' : profile
  }
  
  return render(request, 'vendor/v_profile.html', context)
