from django import forms

from accounts.validators import image_type_validator
from .models import Category, FoodItem

class CategoryForm(forms.ModelForm):
  class Meta:
    model = Category
    fields = ['category_name', 'description']
    
class FoodItemForm(forms.ModelForm):
  image = forms.FileField(widget=forms.FileInput(attrs={'class':'w-100'}), validators=[image_type_validator])
  class Meta:
    model = FoodItem
    fields = ['food_title', "category", 'description', "image", "price", 'is_available']
    
  def __init__(self, *args, **kwargs):
    vendor = kwargs.pop('vendor', None)  # Pass vendor when initializing form
    super(FoodItemForm, self).__init__(*args, **kwargs)
    if vendor:
      self.fields['category'].queryset = Category.objects.filter(vendor=vendor)
    
    
  