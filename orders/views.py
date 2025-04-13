from collections import defaultdict
from decimal import Decimal
import json
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
import razorpay

from accounts.utils import send_notification
from marketplace.models import Cart, Tax
from marketplace.context_processor import get_cart_amount
from orders.forms import OrderForm
from orders.models import Order, OrderedFood, Payment
from orders.utils import generate_order_number
from django.conf import settings


client = razorpay.Client(auth=(settings.RZP_KEY_ID, settings.RZP_KEY_SECRET))

def update_tax_details_per_vendor(order_info_per_vendor, dynamic_tax):
  for vendor_id in order_info_per_vendor.keys():
    subtotal = order_info_per_vendor[vendor_id]['subtotal']
    order_info_per_vendor[vendor_id]['grand_total'] = subtotal
    for t in dynamic_tax:
      tax_type = t.tax_type
      tax_percentage = float(t.tax_percentage)
      tax_amount = round((tax_percentage*subtotal)/100, 2)
      order_info_per_vendor[vendor_id]['tax_details'].append({
        'type': tax_type,
        'percentage': float(tax_percentage),
        'amount': float(tax_amount)
      })
      order_info_per_vendor[vendor_id]['grand_total'] += tax_amount


@login_required(login_url='login')
def place_order(request):
  cart_queryset = Cart.objects.filter(user=request.user).select_related('food_item')
  
  cart_items = list(cart_queryset)
  
  if len(cart_items) <= 0:
    return redirect('marketplace')
  
  vendor_ids = []
  
  # tax details per vendor and unique vendor per order
  order_info_per_vendor = defaultdict(lambda: {
      'subtotal': 0.0,
      'grand_total': 0.0,
      'tax_details': []
  }) 

  dynamic_tax = Tax.objects.filter(is_active=True)
  for item in cart_items:
    v_id = item.food_item.vendor.id
    if v_id not in vendor_ids:
      vendor_ids.append(v_id)
    order_info_per_vendor[v_id]['subtotal'] += float(item.food_item.price) * item.quantity
  update_tax_details_per_vendor(order_info_per_vendor, dynamic_tax)
  
  cart_amount_details = get_cart_amount(request)

  grand_total = cart_amount_details['grand_total']
  tax_details = cart_amount_details['tax_details']
  
  total_tax = sum(tax['amount'] for tax in tax_details)
  
  context = {
    'cart_amount' : cart_amount_details
  }
  
  if request.method == 'POST':
    form = OrderForm(request.POST)
    if form.is_valid():
      order = Order()
      order.first_name = form.cleaned_data['first_name']
      order.last_name = form.cleaned_data['last_name']
      order.phone = form.cleaned_data['phone']
      order.email = form.cleaned_data['email']
      order.address = form.cleaned_data['address']
      order.country = form.cleaned_data['country']
      order.state = form.cleaned_data['state']
      order.city = form.cleaned_data['city']
      order.pincode = form.cleaned_data['pincode']
      order.user = request.user
      order.total = grand_total
      order.tax_data = json.dumps(tax_details)
      order.total_data = json.dumps(order_info_per_vendor)
      order.total_tax = total_tax
      order.payment_method =  request.POST.get('payment-method')
      order.save()
      
      # RazorPay Implementation
      if order.payment_method == 'RazorPay':
        razorpay_order = client.order.create({
          'amount': float(order.total * 100),  # in paise
          'currency': 'INR',
          'receipt': 'receipt #'+order.order_number,
          "notes":{
            'key1': 'value3',
            'key2': 'value2'
          }
        })
        razorpay_order_id = razorpay_order['id']
        context['razorpay_order_id'] = razorpay_order_id
        context['RZP_KEY_ID'] = settings.RZP_KEY_ID
        context['rzp_amount'] = float(order.total * 100)
        
      order.vendors.add(*vendor_ids) # Adding Vendors

      order_number = generate_order_number(order.id)
      Order.objects.filter(id=order.id).update(order_number=order_number)
      # cart_items = Cart.objects.filter(user=request.user).delete()
      cart_items = Cart.objects.filter(user=request.user)
      # messages.success(request, 'Successfully placed Order.')
      order.order_number = order_number
      context['order'] = order
      context['cart_items'] = cart_items

      return render(request, 'orders/place_order.html', context) 
    else:
      print(form.errors)
      messages.error(request, 'Order is not successfull.')
  
  return render(request, 'orders/place_order.html', context)

@login_required(login_url='login')
def payments(request):
  if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == 'POST':
    order_number = request.POST.get('order_number')
    transaction_id = request.POST.get('transaction_id')
    payment_method = request.POST.get('payment_method')
    status = request.POST.get('status')

    try:
      with transaction.atomic():  # ensures rollback on error
        order = Order.objects.get(user=request.user, order_number=order_number)

        payment = Payment.objects.create(
          user=request.user,
          amount=order.total,
          transaction_id=transaction_id,
          payment_method=payment_method,
          status=status
        )

        order.payment = payment
        order.is_ordered = True
        order.save()

        cart_items = Cart.objects.filter(user=request.user).select_related('food_item', 'food_item__vendor__user')
        
        OrderedFood.objects.bulk_create([
          OrderedFood(
            order=order,
            payment=payment,
            fooditem=item.food_item,
            quantity=item.quantity,
            user=request.user,
            price=item.food_item.price,
            amount=item.food_item.price * item.quantity
          )
          for item in cart_items
        ])

    except Order.DoesNotExist:
      return JsonResponse({'error': 'Order not found'}, status=404)

    # Async or delayed task recommended here
    user_email_context = {
      'user': request.user,
      'order': order,
      'to_email': order.email
    }
    send_notification('Order Confirmation', 'orders/emails/order_confirmation_email.html', user_email_context)

    vendor_emails = list(set(item.food_item.vendor.user.email for item in cart_items))
    vendor_email_context = {
      'user': request.user,
      'order': order,
      'to_email': vendor_emails
    }
    send_notification('You have received a new Order', 'orders/emails/order_received.html', vendor_email_context)

    # Optional: clear cart
    # cart_items.delete()

    return JsonResponse({
        'order_number': order_number,
        'transaction_id': transaction_id
    })

  return HttpResponse('Payment View')

def order_complete(request):
  order_number = request.GET.get('order_no')
  transaction_id = request.GET.get('tran_id')
  
  try:
    order = Order.objects.get(order_number=order_number, payment__transaction_id=transaction_id, is_ordered=True)
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
    return render(request, 'orders/order_complete.html', context)
  except:
    return redirect('home')