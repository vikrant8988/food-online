from django.urls import (
    path,
    include
)

# custom imports
from . import views

urlpatterns = [
    path('', views.marketplace, name="marketplace"),
    
    # Add to Cart
    path('add-to-cart/<int:food_id>/', views.add_to_cart, name='add_to_cart'),
    # decrease from Cart
    path('decrease-cart/<int:food_id>/', views.decrease_cart, name='decrease_cart'),
    # delete cart item
    path('delete-cart/<int:cart_id>/', views.delete_cart, name='delete_cart'),
    
    path('<slug:vendor_slug>/', views.vendor_detail, name="vendor_detail"),

]
