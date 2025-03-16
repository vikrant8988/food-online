from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.db.models import Prefetch, Q, Subquery
from django.contrib.auth.decorators import login_required

from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.measure import D  # ``D`` is a shortcut for ``Distance``
from django.contrib.gis.db.models.functions import Distance

from marketplace.context_processor import get_cart_count, get_cart_amount
from .models import Cart
from menu.models import Category, FoodItem
from vendor.models import Vendor


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

def search(request):

  if not 'address' in request.GET:
    return redirect('marketplace')
  
  # address = request.GET.get('address')
  latitude = request.GET.get('lat')
  longitude = request.GET.get('long')
  radius = request.GET.get('radius')
  keyword = request.GET.get('keyword', '')

  # Get vendor IDs that have food items matching the keyword
  query_vendor_by_food_title = FoodItem.objects.filter(
    food_title__icontains=keyword,
    is_available=True
  ).values_list('vendor', flat=True).distinct()

  # Base queryset: vendors matching food or vendor name
  vendor_queryset = Vendor.objects.filter(
    Q(id__in=query_vendor_by_food_title) |
    Q(vendor_name__icontains=keyword),
    is_approved=True,
    user__is_active=True
  )

  # Apply distance filter only if location-based search is provided
  if latitude and longitude and radius:
    try:
      pnt = GEOSGeometry("POINT({} {})".format(longitude, latitude), srid=4326)
      vendor_queryset = vendor_queryset.filter(
        user_profile__location__distance_lte=(pnt, D(km=float(radius)))
      ).annotate(distance=Distance("user_profile__location", pnt)).order_by('distance')
    except (ValueError, TypeError):
      pass  # handle bad input gracefully if needed

  vendor_list = list(vendor_queryset)
  context = {
    'vendors': vendor_list,
    'vendor_count': len(vendor_list)
  }

  return render(request, 'marketplace/listings.html', context)
