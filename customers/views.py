import json
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models.functions import Concat
from django.db.models import Value

from accounts.forms import UserInfoForm, UserProfileForm
from accounts.models import UserProfile
from orders.models import Order, OrderedFood

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

@login_required()
def my_orders(request):
  orders = Order.objects.filter(user=request.user) \
    .order_by('-updated_at') \
    .annotate(name=Concat('first_name', Value(' '), 'last_name')) \
    .values('order_number', 'created_at', 'total', 'total_tax', 'status', 'name')
    
  # print(orders.query)

  context ={
    'orders': orders,
  }
  return render(request, 'customers/my_orders.html', context)

@login_required()
def order_details(request, order_number):
  try:
    order = Order.objects.get(order_number=order_number)
    ordered_food = OrderedFood.objects.filter(order=order)
    
    order_details = {
      'subtotal': round(order.total - order.total_tax,2),
      'grand_total': round(order.total, 2),
      'tax_details': json.loads(order.tax_data)
    }
    
    context = {
      'order': order,
      'ordered_food': ordered_food,
      'order_details': order_details
    }
    return render(request, 'customers/order_details.html', context)
  except:
    return redirect('c_order')
