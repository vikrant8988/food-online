from django.contrib import admin
from .models import Vendor


class CustomVendorAdmin(admin.ModelAdmin):
  list_display = ('vendor_name', 'user', 'is_approved', 'created_at')
  list_display_links = ('vendor_name','user')
  list_editable = ('is_approved',)

# Register your models here.
admin.site.register(Vendor, CustomVendorAdmin)
