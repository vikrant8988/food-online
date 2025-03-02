from django.shortcuts import redirect, render
from .forms import UserForm
from .models import (
  User,
  UserProfile
)
from django.contrib import messages
from vendor.forms import VendorForm

# Create your views here.
def registerUser(request):
  if request.method == 'POST':
    form = UserForm(request.POST)
    if form.is_valid():
      password = form.cleaned_data['password']
      user = form.save(commit=False)
      user.role = User.CUSTOMER
      user.set_password(password)
      user.save()
      messages.success(request, 'Your account has been successfully registered.')
      return redirect("home")
  else:
    form = UserForm()
  
  context = {
    'form' : form,
  }
  
  return render(request, 'accounts/registerUser.html', context)


def registerVendor(request):
  
  if request.method == 'POST':
    user_form = UserForm(request.POST)
    vendor_form = VendorForm(request.POST, request.FILES)
    
    if user_form.is_valid() and vendor_form.is_valid():
      first_name = user_form.cleaned_data['first_name']
      last_name = user_form.cleaned_data['last_name']
      username = user_form.cleaned_data['username']
      email = user_form.cleaned_data['email']
      password = user_form.cleaned_data['password']
      user = User.objects.create_user(first_name=first_name, last_name=last_name, username=username,email=email,password=password)
      user.role = User.VENDOR
      user.save()
      
      vendor_form = vendor_form.save(commit=False)
      vendor_form.user = user
      user_profile = UserProfile.objects.get(user=user)
      vendor_form.user_profile = user_profile
      vendor_form.save()
      
      messages.success(request, 'Your account has been registered successfully! It will be activated after approval.')
      return redirect("home")
    else:
      print("Error in Vendor Form : User -> ", user_form.errors)
      print("Error in Vendor forms :  Vendor - > ", vendor_form.errors)
  else:
    user_form = UserForm()
    vendor_form =  VendorForm()

  context = {
    'user_form' : user_form,
    'vendor_form' : vendor_form
  }
  return render(request, 'accounts/registerVendor.html', context)
