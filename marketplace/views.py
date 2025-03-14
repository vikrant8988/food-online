from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render

from marketplace.context_processor import get_cart_count, get_cart_amount

from .models import Cart
from menu.models import Category, FoodItem
from vendor.models import Vendor
from django.db.models import Prefetch
from django.contrib.auth.decorators import login_required

# Create your views here.

def marketplace(request):
  vendors = Vendor.objects.filter(is_approved=True, user__is_active=True)
  vendor_count = vendors.count()
  context = {
    'vendors': vendors,
    'vendor_count': vendor_count,
  }
  return render(request, 'marketplace/listings.html', context)

def vendor_detail(request, vendor_slug):
  vendor = get_object_or_404(Vendor, slug=vendor_slug)
  categories = Category.objects.filter(vendor=vendor).prefetch_related(
      Prefetch(
        'fooditems',
        queryset=FoodItem.objects.filter(is_available=True)
      )
    )
  
  if request.user.is_authenticated:
    cart_items = Cart.objects.filter(user=request.user).select_related('food_item')
  else:
    cart_items =  []
  
  context = {
    'vendor': vendor,
    'categories': categories,
    'cart_items' : cart_items
  }
  return render(request, 'marketplace/vendor_detail.html', context)


def add_to_cart(request, food_id):
  if request.user.is_authenticated:
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
      # Check If food item exists
      try:
        food_item = FoodItem.objects.get(id=food_id)
        # Check if user has already added same food item to cart
        try:
          check_cart = Cart.objects.get(user=request.user, food_item=food_item)
          check_cart.quantity += 1
          check_cart.save()
          response = {
            'status':  'success',
            'message': 'Food quantity increased.',
            'cart_counter': get_cart_count(request),
            'qty': check_cart.quantity,
            'cart_amount': get_cart_amount(request)
          }
        except:
          check_cart = Cart.objects.create(user=request.user, food_item=food_item, quantity=1)
          response = {
            'status':  'success',
            'message': 'Food Item added to cart.',
            'cart_counter': get_cart_count(request),
            'qty': check_cart.quantity
          }
      except:
        response = {
          'status':  'failed',
          'message': 'This Food Item does not exists.'
        }
    else:
      response = {
      'status':  'failed',
      'message': 'invalid request.'
    }
  else:
    response = {
      'status':  'login_required',
      'message': 'Please Login to continue.'
    }
  return JsonResponse(response)

def decrease_cart(request, food_id):
  if request.user.is_authenticated:
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
      # Check If food item exists
      try:
        food_item = FoodItem.objects.get(id=food_id)
        # Check if user has already added same food item to cart
        try:
          check_cart = Cart.objects.get(user=request.user, food_item=food_item)
          # decrease the quantity
          if check_cart.quantity > 1:
            check_cart.quantity -= 1
            check_cart.save()
          else:
            check_cart.delete()
            check_cart.quantity = 0
          response = {
            'status':  'success',
            'cart_counter': get_cart_count(request),
            'qty': check_cart.quantity,
            'cart_amount': get_cart_amount(request)
          }
        except:
          response = {
            'status':  'failed',
            'message': 'You do not have this item in cart!'
          }
      except:
        response = {
          'status':  'failed',
          'message': 'This Food Item does not exists.'
        }
    else:
      response = {
      'status':  'failed',
      'message': 'invalid request.'
    }
  else:
    response = {
      'status':  'login_required',
      'message': 'Please Login to continue.'
    }
  return JsonResponse(response)

@login_required(login_url='login')
def cart(request):
  cart_items = Cart.objects.filter(user=request.user).order_by('created_at').select_related('food_item', 'food_item__vendor')
  context = {
    'cart_items': cart_items
  }
  return render(request, 'marketplace/cart.html', context)

def delete_cart(request, cart_id):
  if request.user.is_authenticated:
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
      # Check If food item exists
      try:
        cart_item = Cart.objects.get(user=request.user, id=cart_id)
        if cart_item:
          cart_item.delete()
          response = {
            'status':  'success',
            'message': 'cart item is deleted.',
            'cart_counter': get_cart_count(request),
            'cart_amount': get_cart_amount(request)
          }
      except:
        response = {
          'status':  'failed',
          'message': 'This Cart Item does not exists.'
        }
    else:
      response = {
      'status':  'failed',
      'message': 'invalid request.'
    }
  return JsonResponse(response)