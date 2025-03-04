from django.urls import (
    path
)

from . import views
from accounts import views as account_views

urlpatterns = [
    path('', account_views.vendorDashboard, name="vendor"),
    path('profile/', views.v_profile, name="v_profile"),
]