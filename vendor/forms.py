from django import forms
from .models import Vendor
from accounts.validators import image_type_validator

class VendorForm(forms.ModelForm):
  vendor_license = forms.FileField(widget=forms.FileInput(), validators=[image_type_validator])
  class Meta:
    model = Vendor
    fields = ["vendor_name", "vendor_license"]
    
    