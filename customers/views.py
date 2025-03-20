from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from accounts.forms import UserInfoForm, UserProfileForm
from accounts.models import UserProfile

# Create your views here.

@login_required()
def c_profile(request):
  customer = UserProfile.objects.get(user=request.user)
  customer.user=request.user
  
  if request.method == 'POST':
    profile_form = UserProfileForm(request.POST, request.FILES, instance=customer)
    user_form = UserInfoForm(request.POST, instance=request.user)
    
    if profile_form.is_valid() and user_form.is_valid():
      profile_form.save()
      user_form.save()
      messages.success(request, 'Profile updated')
      return redirect('c_profile')
    else:
      print(profile_form.errors)
      print(user_form.errors)
      
  else:
    profile_form = UserProfileForm(instance=customer)
    user_form = UserInfoForm(instance=request.user)
  
  context={
    'profile_form': profile_form,
    'user_form': user_form,
    'customer': customer
  }
  return render(request, 'customers/c_profile.html', context)
