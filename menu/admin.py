from django.contrib import admin

from .models import FoodItem, Category

class CategoryAdmin(admin.ModelAdmin):
  prepopulated_fields = {'slug': ('category_name',)}
  list_display =('category_name', 'vendor', 'updated_at')
  search_fields = ('category_name', 'vendor__vendor_name')
  
class FoodItemAdmin(admin.ModelAdmin):
  prepopulated_fields = {'slug': ('food_title',)}
  list_display =('food_title', 'vendor', 'category', 'price','is_available', 'updated_at')
  search_fields = ('food_title', 'category__category_name', 'vendor__vendor_name')
  list_filter = ('is_available',)

# Register your models here.
admin.site.register(Category, CategoryAdmin)
admin.site.register(FoodItem, FoodItemAdmin)
