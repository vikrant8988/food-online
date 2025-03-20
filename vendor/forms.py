from datetime import datetime
from django import forms
from .models import Vendor, OpeningHour
from accounts.validators import image_type_validator

class VendorForm(forms.ModelForm):
  vendor_license = forms.FileField(widget=forms.FileInput(), validators=[image_type_validator])
  class Meta:
    model = Vendor
    fields = ["vendor_name", "vendor_license"]
    
class OpeningHourForm(forms.ModelForm):
  class Meta:
    model = OpeningHour
    fields = ["day", "from_hour", "to_hour", "is_closed"]
    
  def clean(self):
    cleaned_data = super().clean()
    from_hour_str = cleaned_data.get("from_hour")
    to_hour_str = cleaned_data.get("to_hour")
    is_closed = cleaned_data.get("is_closed")

    if not is_closed:
      if not from_hour_str or not to_hour_str:
          raise forms.ValidationError("Please select both opening and closing hours.")
      try:
          from_hour = datetime.strptime(from_hour_str, "%I:%M %p").time()
          to_hour = datetime.strptime(to_hour_str, "%I:%M %p").time()
      except ValueError:
          raise forms.ValidationError("Invalid time format. Please select valid hours.")

      if from_hour >= to_hour:
          raise forms.ValidationError("Opening hour must be earlier than closing hour.")

    return cleaned_data
    
    