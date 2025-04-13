from django.urls import (
    path
)

from . import views
from accounts import views as account_views

urlpatterns = [
    path('', account_views.vendorDashboard, name="vendor"),
    path('profile/', views.v_profile, name="v_profile"),
    path('menu-builder/', views.menu_builder, name="menu_builder"),
    path('menu-builder/category/<pk>', views.food_items_by_category, name="food_items_by_category"),
    
    # Category CRUD
    path('menu-builder/category/add/', views.add_category, name="add_category"),
    path('menu-builder/category/edit/<int:pk>', views.edit_category, name="edit_category"),
    path('menu-builder/category/delete/<int:pk>', views.delete_category, name="delete_category"),
    
    # Food CRUD
    path('menu-builder/food/add/', views.add_food, name="add_food"),
    path('menu-builder/food/edit/<int:pk>', views.edit_food, name="edit_food"),
    path('menu-builder/food/delete/<int:pk>', views.delete_food, name="delete_food"),
    
    # Opening Hour CRUD
    path('opening-hours/', views.opening_hours, name="opening_hours"),
    path('opening-hours/add/', views.add_opening_hours, name="add_opening_hours"),
    path('opening-hours/delete/<int:pk>', views.delete_opening_hours, name="delete_opening_hours"),
    
    # Order Details
    path('order_details/<int:order_number>/', views.order_details, name="v_order_details"),
    path('orders/', views.orders, name="v_orders"),
]