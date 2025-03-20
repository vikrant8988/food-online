from django.contrib import admin
from .models import Vendor, OpeningHour


class CustomVendorAdmin(admin.ModelAdmin):
  list_display = ('vendor_name', 'user', 'is_approved', 'created_at')
  list_display_links = ('vendor_name','user')
  list_editable = ('is_approved',)
  
class OpeningHourAdmin(admin.ModelAdmin):
  list_display = ('vendor', 'day', 'is_closed', 'from_hour', 'to_hour')


# Register your models here.
admin.site.register(Vendor, CustomVendorAdmin)
admin.site.register(OpeningHour, OpeningHourAdmin)
