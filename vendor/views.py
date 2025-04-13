from decimal import Decimal
import json
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.db.models.functions import Concat
from django.db.models import Value
from django.contrib import messages
from django.template.defaultfilters import slugify

from marketplace.models import Tax
from menu.forms import CategoryForm, FoodItemForm
from orders.models import Order, OrderedFood
from .forms import VendorForm, OpeningHourForm
from accounts.forms import UserProfileForm
from .models import Vendor, OpeningHour
from accounts.models import UserProfile
from menu.models import Category, FoodItem


def get_vendor(request):
  vendor = Vendor.objects.get(user=request.user)
  return vendor

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

def menu_builder(request):
  vendor = get_vendor(request)
  categories = Category.objects.filter(vendor=vendor).order_by('created_at')
  category_form = CategoryForm()
  food_form = FoodItemForm(vendor=vendor)
  context = {
    'categories' : categories,
    'category_form' : category_form,
    'food_form' : food_form
  }
  return render(request, 'vendor/menu_builder.html', context)

def food_items_by_category(request, pk=None):
  vendor = get_vendor(request)
  category = get_object_or_404(Category, pk=pk)
  food_items = FoodItem.objects.filter(vendor=vendor, category=category)
  context= {
    'food_items': food_items,
    'category' : category
  }
  
  return render(request, 'vendor/food_items_by_category.html', context)

def add_category(request):
  if request.method == 'POST':
    form = CategoryForm(request.POST)
    if form.is_valid():
      category_name = form.cleaned_data['category_name']
      category = form.save(commit=False)
      category.vendor = get_vendor(request)
      category.slug = slugify(category_name) + str(category.vendor.vendor_name.lower())
      category.save()
      messages.success(request, 'Category Added Successfully.')
      return redirect('menu_builder')  # redirect on success
    else:
      vendor = get_vendor(request)
      categories = Category.objects.filter(vendor=vendor)
      messages.error(request, 'Add Unsuccessful. Please fix the errors below.')
      context = {
        'category_form': form,
        'categories': categories,
        'show_category_modal': True,
      }
      return render(request, 'vendor/menu_builder.html', context)

  return redirect('menu_builder')
  
  
def edit_category(request, pk=None):
  category = get_object_or_404(Category, pk=pk)
  if request.method == 'POST':
    form = CategoryForm(request.POST, instance=category)
    if form.is_valid():
      category_name = form.cleaned_data['category_name']
      category = form.save(commit=False)
      category.vendor = get_vendor(request)
      category.slug = slugify(category_name) + str(category.vendor.vendor_name.lower())
      category.save()
      messages.success(request, 'Category Added Successfully.')
      return redirect('menu_builder')  # redirect on success
    else:
      print(form.errors)
  else:
    form  = CategoryForm(instance=category)
    
  context= {
    'form': form,
    'category': category
  }
  
  return render(request, 'vendor/edit_category.html', context)

def delete_category(request, pk=None):
  category = get_object_or_404(Category, pk=pk)
  category.delete()
  messages.success(request, 'Category Deleted Successfully.')
  return redirect('menu_builder')  # redirect on success


def add_food(request):
  if request.method == 'POST':
    form = FoodItemForm(request.POST, request.FILES)
    if form.is_valid():
      food_title = form.cleaned_data['food_title']
      food_item = form.save(commit=False)
      food_item.vendor = get_vendor(request)
      food_item.slug = slugify(food_title) + str(food_item.vendor.vendor_name.lower())
      food_item.save()
      messages.success(request, 'Category Added Successfully.')
      return redirect('food_items_by_category', food_item.category.id)  # redirect on success
    else:
      vendor = get_vendor(request)
      categories = Category.objects.filter(vendor=vendor)
      messages.error(request, 'Add Unsuccessful. Please fix the errors below.')
      context = {
        'food_form': form,
        'categories': categories,
        'show_category_modal': True,
      }
      return render(request, 'vendor/menu_builder.html', context)

  return redirect('menu_builder')

def edit_food(request, pk=None):
  food = get_object_or_404(FoodItem, pk=pk)
  if request.method == 'POST':
    form = FoodItemForm(request.POST, request.FILES, instance=food)
    if form.is_valid():
      food_title = form.cleaned_data['food_title']
      form = form.save(commit=False)
      form.vendor = get_vendor(request)
      form.slug = slugify(food_title) + str(form.vendor.vendor_name.lower())
      form.save()
      messages.success(request, 'Category Added Successfully.')
      return redirect('food_items_by_category', food.category.id)  # redirect on success
    else:
      print(form.errors)
    
  else:
    form = FoodItemForm(instance=food)
    
  context = {
    'form': form,
    'food': food
  }

  return render(request, 'vendor/edit_food.html', context)


def delete_food(request, pk=None):
  food = get_object_or_404(FoodItem, pk=pk)
  food.delete()
  messages.success(request, 'Food Item Deleted Successfully.')
  return redirect('food_items_by_category', food.category.id)  # redirect on success

def opening_hours(request):
  vendor = Vendor.objects.get(user=request.user)
  opening_hours = OpeningHour.objects.filter(vendor=vendor).order_by('day')
  opening_hour_form = OpeningHourForm()
  context= {
    'opening_hours': opening_hours,
    'form' : opening_hour_form
  }
  return render(request, 'vendor/opening_hour.html', context)

def add_opening_hours(request):
  if request.user.is_authenticated:
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == 'POST':
      day = request.POST.get('day')
      from_hour = request.POST.get('from_hour')
      to_hour = request.POST.get('to_hour')
      is_closed = request.POST.get('is_closed') == 'True'
      
      isValid = day and (is_closed or (from_hour and to_hour))
      
      if not isValid:
        return JsonResponse({'status': 'failed', 'message': 'fields are missing'}, status=400)
      
      opening_hours_data = {
        'from_hour': from_hour,
        'to_hour': to_hour,
        'is_closed': is_closed
      }
      
      try:
        business_hour, created = OpeningHour.objects.update_or_create(
          vendor=get_vendor(request),
          day=int(day),
          defaults=opening_hours_data
        )

        data = {
          'from_hour': business_hour.from_hour,
          'to_hour': business_hour.to_hour,
          'is_closed': business_hour.is_closed,
          'day': business_hour.get_day_display(),
          'id': business_hour.id
        }

        if created:
          return JsonResponse({'status': 'success', 'message': 'Opening hour created', 'data':data}, status=201)
        else:
          return JsonResponse({'status': 'success', 'message': 'Opening hour updated', 'data':data}, status=200)
      except Exception as e:
        print(f"Failure: {str(e)}")
        return JsonResponse({'status': 'failed', 'message': 'Invalid form data'}, status=400)
    else:
      print('Error : Business Hours')
  return JsonResponse({'status': 'failed', 'message': 'Unauthorized'}, status=401)


def delete_opening_hours(request, pk):
    if request.user.is_authenticated:
      if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        business_hour = get_object_or_404(OpeningHour, pk=pk)
        business_hour.delete()
        return JsonResponse({'status':'success', 'id':pk})
        
def order_details(request, order_number):
  try:
    vendor = Vendor.objects.get(user = request.user)
      
    order = Order.objects.get(order_number=order_number)
    ordered_food = OrderedFood.objects.filter(order=order, fooditem__vendor=vendor)
    order_amount_details = json.loads(order.total_data).get(str(vendor.id), {}) if order.total_data else {}
    print(order_amount_details)
    
    context = {
      'vendor': vendor,
      'order': order,
      'ordered_food': ordered_food,
      'order_details': order_amount_details
    }
    return render(request, 'vendor/order_details.html', context)
  except:
    return redirect('v_orders')
  
def orders(request):
  vendor = Vendor.objects.get(user = request.user)
  
  orders = Order.objects.filter(vendors__in=[vendor.id], is_ordered=True) \
            .order_by('-created_at')

  # orders = Order.objects.filter(vendors__in=[vendor.id], is_ordered=True) \
  #   .order_by('-created_at') \
  #   .annotate(name=Concat('first_name', Value(' '), 'last_name')) \
  #   .values('order_number', 'created_at', 'total', 'total_tax', 'status', 'name')
    
  # order_details = json.loads(order.total_data).get(vendor.id,{})
  # order.total = order_details['grand_total']
    
  # print(orders.query)

  context ={
    'orders': orders,
  }
  return render(request, 'vendor/orders.html', context)
