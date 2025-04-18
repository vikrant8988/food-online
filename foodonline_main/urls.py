
from django.contrib import admin
from django.urls import (
    path,
    include
)
from django.conf import settings
from django.conf.urls.static import static

from . import views
from marketplace import views as marketplaceViews

urlpatterns = [
    path('admin/', admin.site.urls),
    
    path('marketplace/', include('marketplace.urls')),
    
    # cart
    path('cart/', marketplaceViews.cart, name='cart'),
    
    # search
    path('search/', marketplaceViews.search, name='search'),
    
    # checkout
    path('checkout/', marketplaceViews.checkout, name='checkout'),
    
    # order
    path('place_order/', include('orders.urls')),
    
    path('', views.home, name="home"),
    path('', include('accounts.urls')),
    
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
