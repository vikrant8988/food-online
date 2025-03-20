from django import forms
from .models import User, UserProfile
from .validators import image_type_validator

class UserForm(forms.ModelForm):
  password = forms.CharField(widget=forms.PasswordInput)
  confirm_password = forms.CharField(widget=forms.PasswordInput)
  class Meta:
    model = User
    fields = ["first_name", "last_name", "username", "email", "phone_number", "password"]
    
  def clean(self):
    cleaned_data = super(UserForm, self).clean()
    password = cleaned_data.get('password')
    confirm_password = cleaned_data.get('confirm_password')
    
    if password != confirm_password:
      raise forms.ValidationError(
        "Password does not match"
      )
      
class UserProfileForm(forms.ModelForm):
  address_line = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'start typing....', 'required':'required'}))
  profile_picture = forms.FileField(widget=forms.FileInput(), validators=[image_type_validator], required=False)
  cover_photo = forms.FileField(widget=forms.FileInput(), validators=[image_type_validator], required=False)
  
  # latitude = forms.CharField(widget=forms.TextInput(attrs={'readonly': 'readonly'}))
  # longitude = forms.CharField(widget=forms.TextInput(attrs={'readonly': 'readonly'}))
  latitude = forms.CharField(widget=forms.TextInput())
  longitude = forms.CharField(widget=forms.TextInput())
  class Meta:
    model = UserProfile
    fields = ["profile_picture", "cover_photo", "address_line", "country", "state", "city", "pincode", "latitude", "longitude"]

class UserInfoForm(forms.ModelForm):
  class Meta:
    model = User
    fields = ["first_name", "last_name", "phone_number"]
  
    
    