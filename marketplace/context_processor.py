from .models import Cart
from menu.models import FoodItem
from django.db.models import Sum

def get_cart_count(request):
  cart_summary = {
    'cart_count' : 0
  }
  
  if request.user.is_authenticated:
    try:
      total_quantity  =Cart.objects.filter(user=request.user).aggregate(total=Sum('quantity'))['total']
      cart_summary['cart_count'] = total_quantity or 0  # Fallback to 0 if total is None
    except:
      pass
  return cart_summary

def get_cart_amount(request):
  subtotal = 0
  tax = 0
  grand_total = 0
  if request.user.is_authenticated:
    cart_items = Cart.objects.filter(user=request.user)
    for item in cart_items:
      food_item = FoodItem.objects.get(pk=item.food_item.id)
      subtotal += (food_item.price * item.quantity)
      
    grand_total = subtotal + 0
    
  return dict(subtotal=subtotal, tax=tax, grand_total=grand_total)