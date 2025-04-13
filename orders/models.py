import json
from django.db import models
from accounts.models import User
from menu.models import FoodItem
from vendor.models import Vendor
from crequest.middleware import CrequestMiddleware

class Payment(models.Model):
  PAYMENT_METHOD = (
    ('PayPal', 'PayPal'),
    ('RazorPay', 'RazorPay'), # Only for Indian Students.
  )
  user = models.ForeignKey(User, on_delete=models.CASCADE)
  transaction_id = models.CharField(max_length=100)
  payment_method = models.CharField(choices=PAYMENT_METHOD, max_length=100)
  amount = models.FloatField()
  status = models.CharField(max_length=100)
  created_at = models.DateTimeField(auto_now_add=True)

  def __str__(self):
    return self.transaction_id


class Order(models.Model):
  STATUS = (
    ('New', 'New'),
    ('Accepted', 'Accepted'),
    ('Completed', 'Completed'),
    ('Cancelled', 'Cancelled'),
  )

  user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
  payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, blank=True, null=True)
  vendors = models.ManyToManyField(Vendor, blank=True)
  order_number = models.CharField(max_length=20)
  first_name = models.CharField(max_length=50)
  last_name = models.CharField(max_length=50)
  phone = models.CharField(max_length=15, blank=True)
  email = models.EmailField(max_length=50)
  address = models.CharField(max_length=200)
  country = models.CharField(max_length=25, blank=True)
  state = models.CharField(max_length=25, blank=True)
  city = models.CharField(max_length=50)
  pincode = models.CharField(max_length=10)
  total = models.FloatField()
  tax_data = models.JSONField(blank=True, help_text = "Data format: [{'type': tax_type,'percentage': tax_percentage,'amount': tax_amount}]", null=True)
  total_data = models.JSONField(blank=True, null=True, help_text = "Data format: {'vendor_id':{'subtotal':'subtotal','grand_total':grand_total, 'tax_details':[{'type': tax_type,'percentage': tax_percentage,'amount': tax_amount}]}}")
  total_tax = models.FloatField()
  payment_method = models.CharField(max_length=25)
  status = models.CharField(max_length=15, choices=STATUS, default='New')
  is_ordered = models.BooleanField(default=False)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

  # Concatenate first name and last name
  @property
  def name(self):
    return f'{self.first_name} {self.last_name}'
  
  def order_placed_to(self):
    return ', '.join([str(v_name) for v_name in self.vendors.all()])
  
  def get_total_by_vendor(self):
    request = CrequestMiddleware.get_request()
    vendor = Vendor.objects.only('id').get(user=request.user)
    order_details = json.loads(self.total_data).get(str(vendor.id), {}) if self.total_data else {}
    return order_details.get('grand_total',0)

  def __str__(self):
    return self.order_number


class OrderedFood(models.Model):
  order = models.ForeignKey(Order, on_delete=models.CASCADE)
  payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, blank=True, null=True)
  user = models.ForeignKey(User, on_delete=models.CASCADE)
  fooditem = models.ForeignKey(FoodItem, on_delete=models.CASCADE)
  quantity = models.IntegerField()
  price = models.FloatField()
  amount = models.FloatField()
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

  def __str__(self):
    return self.fooditem.food_title