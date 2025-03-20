from .models import Cart, Tax
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
  tax_details = []
  if request.user.is_authenticated:
    cart_items = Cart.objects.filter(user=request.user)
    for item in cart_items:
      food_item = FoodItem.objects.get(pk=item.food_item.id)
      subtotal += (food_item.price * item.quantity)
      
    dynamic_tax = Tax.objects.filter(is_active=True)
    
    grand_total = subtotal
    
    for t in dynamic_tax:
      tax_type = t.tax_type
      tax_percentage = t.tax_percentage
      tax_amount = round((tax_percentage*subtotal)/100, 2)
      tax_details.append({
        'type': tax_type,
        'percentage': float(tax_percentage),
        'amount': tax_amount
      })
      grand_total += tax_amount

    return {
      'subtotal': subtotal,
      'grand_total': grand_total,
      'tax_details': tax_details
    }