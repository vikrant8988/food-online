from django.shortcuts import redirect, render, get_object_or_404

from menu.forms import CategoryForm

from .forms import VendorForm
from accounts.forms import UserProfileForm
from .models import Vendor
from accounts.models import UserProfile
from django.contrib import messages
from menu.models import Category, FoodItem
from django.template.defaultfilters import slugify

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
  context = {
    'categories' : categories,
    'category_form' : category_form
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
      category.slug = slugify(category_name)
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
      category.slug = slugify(category_name)
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