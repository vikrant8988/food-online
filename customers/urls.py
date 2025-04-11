from django.urls import (
    path,
    include
)

from accounts import views as AccountViews
from . import views

urlpatterns = [
  path('', AccountViews.customerDashboard, name="customer"),
  path('profile/', views.c_profile, name="c_profile"),
  path('my_orders/', views.my_orders, name="c_my_orders"),
  path('order_details/<int:order_number>/', views.order_details, name="c_order_details"),
]