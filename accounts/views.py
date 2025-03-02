from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied

from .forms import UserForm
from .models import (
  User,
  UserProfile
)
from vendor.forms import VendorForm
from .utils import detectUser


def check_role_customer(user):
  if user.role == 1:
    return True
  else:
    raise PermissionDenied

def check_role_vendor(user):
  if user.role == 2:
    return True
  else:
    raise PermissionDenied

# Create your views here.
def registerUser(request):
  if request.user.is_authenticated:
    return redirect('home')
    
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
  if request.user.is_authenticated:
    return redirect('home')
  
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

def login(request):
  if request.user.is_authenticated:
    return redirect('home')
  if request.method == 'POST':
    email = request.POST['email']
    password = request.POST['password']
    
    user = auth.authenticate(email=email, password=password)
    # print(f"email: {email} and password : {password}")
    
    if user is not None:
      auth.login(request, user)
      messages.success(request, "You are now logged in.")
      print("user",user)
      return redirect("myAccount")
    else:
      messages.error(request, "Invalid Login credentials.")
      return redirect("login")
  
  return render(request, 'accounts/login.html')

def logout(request):
  if not request.user.is_authenticated:
    return redirect('login')
  auth.logout(request=request)
  messages.info(request, "You are now logged out.")
  return redirect("login")

@login_required(login_url='login')
def myAccount(request):
  user = request.user
  redirectUrl =  detectUser(user)
  return redirect(redirectUrl)

@login_required(login_url='login')
@user_passes_test(check_role_customer)
def customerDashboard(request):
  return render(request, 'accounts/customerDashboard.html')

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def vendorDashboard(request):
  return render(request, 'accounts/vendorDashboard.html')
