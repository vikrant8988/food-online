from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator

from .forms import UserForm
from .models import (
  User,
  UserProfile
)
from vendor.forms import VendorForm
from vendor.models import Vendor
from .utils import detectUser, send_verification_email

def check_role_customer(user):
  if user.role == User.CUSTOMER:
    return True
  else:
    raise PermissionDenied

def check_role_vendor(user):
  if user.role == User.VENDOR:
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
      
      # send verification email
      email_subject = 'Please activate your account'
      email_template = 'accounts/emails/account_verification_email.html'
      send_verification_email(request, user, email_subject, email_template)
      
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
      
      # send verification email
      email_subject = 'Please activate your account'
      email_template = 'accounts/emails/account_verification_email.html'
      send_verification_email(request, user, email_subject, email_template)
      
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
  vendor = Vendor.objects.get(user = request.user)
  context ={
    'vendor' : vendor
  }
  return render(request, 'accounts/vendorDashboard.html', context)

def activate(request, uidb64, token):
  # activate user by setting is_active=True
  try:
    uid =  urlsafe_base64_decode(uidb64).decode()
    user = User.objects.get(pk=uid)
  except(TypeError, ValueError, OverflowError, User.DoesNotExist):
    user = None
  
  if user is not None and default_token_generator.check_token(user, token):
    user.is_active = True
    user.save()
    
    messages.success(request, "Congratulations! Your account has been successfully activated.")
    return redirect('myAccount')
  else:
    messages.error(request, 'Invalid activation Link')
    return('myAccount')
  
  
def forgot_password(request):
  if request.method == 'POST':
    email = request.POST['email']
    try:
      user = User.objects.get(email__iexact=email)  # Case-insensitive match
      # send reset password email
      email_subject = 'Reset your password'
      email_template = 'accounts/emails/reset_password_email.html'
      send_verification_email(request, user, email_subject, email_template)
      messages.success(request, "We've sent a password reset link to your email address.")
      return redirect('login')
    except User.DoesNotExist:
      messages.error(request, "We couldn't find an account with that email address.")
      return redirect('forgot_password')
  return render(request, 'accounts/forgot_password.html')

def reset_password_validate(request, uidb64, token):
  try:
    uid =  urlsafe_base64_decode(uidb64).decode()
    user = User.objects.get(pk=uid)
  except(TypeError, ValueError, OverflowError, User.DoesNotExist):
    user = None
  
  if user is not None and default_token_generator.check_token(user, token):
    request.session['uid'] = uid
    request.session['reset_token'] = token  # Store Token
    return redirect('reset_password')
  else:
    messages.error(request, 'Invalid activation Link')
    return('myAccount')


def reset_password(request):
  
  uid = request.session.pop('uid', None)  # Get UID from session
  token =request.session.pop('reset_token', None)  # Get Token from session
          

  if not uid or not token:  # If no UID or token, block access
    messages.error(request, "Unauthorized access. Please request a new reset link.")
    return redirect('forgot_password')

  try:
      user = User.objects.get(pk=uid)
  except User.DoesNotExist:
      messages.error(request, "User does not exist.")
      return redirect('forgot_password')

  if not default_token_generator.check_token(user, token):
      messages.error(request, "Invalid or expired token.")
      return redirect('forgot_password')

  if request.method == 'POST':
      password = request.POST['password']
      confirm_password = request.POST['confirm_password']

      if password == confirm_password:
          user.set_password(password)
          user.save()

          # Clear session after successful reset
          

          messages.success(request, "Password reset successfully. Please log in.")
          return redirect('login')
      else:
          messages.error(request, "Passwords do not match.")
          return redirect('reset_password')

  return render(request, 'accounts/forgot_password.html')
