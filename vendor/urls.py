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
    
    path('menu-builder/category/add/', views.add_category, name="add_category"),
    path('menu-builder/category/edit/<int:pk>', views.edit_category, name="edit_category"),
    path('menu-builder/category/delete/<int:pk>', views.delete_category, name="delete_category"),
]