from django.db import models
from django.contrib.auth.models import (
  AbstractBaseUser,
  BaseUserManager
)
from django.contrib.gis.db import models as gismodels
from django.contrib.gis.geos import Point

class UserManager(BaseUserManager):
  def create_user(self, first_name, last_name, username, email, password=None):
    if not email:
      raise ValueError('Email field is mandatory')
    
    if not username:
      raise ValueError('Username field is mandatory')
    
    user = self.model(
      email = self.normalize_email(email),
      username = username,
      first_name = first_name,
      last_name = last_name
    )
    user.set_password(password)
    user.save(using=self._db)
    return user
  
  def create_superuser(self, first_name, last_name, username, email, password=None):
    user =  self.create_user(
      email = self.normalize_email(email),
      username = username,
      first_name = first_name,
      last_name = last_name,
      password=password
    )
    user.is_admin = True
    user.is_active = True
    user.is_staff = True
    user.is_super_admin = True
    user.save(using=self._db)
    
    return user
    

class User(AbstractBaseUser):
  VENDOR = 1
  CUSTOMER = 2
  
  ROLE_CHOICE =(
    (VENDOR, 'Vendor'),
    (CUSTOMER, 'Customer')
  )
  first_name = models.CharField(max_length=50)
  last_name = models.CharField(max_length=50)
  username = models.CharField(max_length=50, unique=True)
  email = models.EmailField(max_length=100, unique=True)
  phone_number = models.CharField(max_length=12, blank=True)
  role = models.PositiveSmallIntegerField(choices=ROLE_CHOICE, blank=True, null=True)
  
  
  # required fields
  date_joined =  models.DateTimeField(auto_now_add=True)
  last_login =  models.DateTimeField(auto_now_add=True)
  created_date =  models.DateTimeField(auto_now_add=True)
  modified_date =  models.DateTimeField(auto_now_add=True)
  is_admin = models.BooleanField(default=False)
  is_active = models.BooleanField(default=False)
  is_staff = models.BooleanField(default=False)
  is_super_admin = models.BooleanField(default=False)
  
  USERNAME_FIELD = 'email'
  REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
  
  objects = UserManager()
  
  def has_perm(self, perm, obj=None):
    return self.is_admin
  
  def has_module_perms(self, app_label):
    return True
  
  def get_role(self):
    if self.role == self.VENDOR:
      return "Vendor"
    elif self.role == self.CUSTOMER:
      return "Customer"
  
  def __str__(self):
    return self.email
  
  
class UserProfile(models.Model):
  user = models.OneToOneField(User, on_delete=models.CASCADE)
  profile_picture = models.ImageField(upload_to='user/profile_pictures', blank=True, null=True)
  cover_photo = models.ImageField(upload_to='user/cover_photos', blank=True, null=True)
  address_line = models.CharField(max_length=250, blank=True, null=True)
  country = models.CharField(max_length=25, blank=True, null=True)
  state = models.CharField(max_length=25, blank=True, null=True)
  city = models.CharField(max_length=25, blank=True, null=True)
  pincode = models.CharField(max_length=6, blank=True, null=True)
  latitude = models.CharField(max_length=20, blank=True, null=True)
  longitude = models.CharField(max_length=20, blank=True, null=True)
  location = gismodels.PointField(blank=True, null=True, srid=4326)
  created_at = models.DateTimeField(auto_now_add=True)
  modified_at = models.DateTimeField(auto_now=True)
  
  def __str__(self):
    return self.user.email
  
  
  def save(self, *args, **kwargs):
    if self.latitude and self.longitude:
      self.location = Point(float(self.longitude), float(self.latitude))
    return super(UserProfile, self).save(*args, **kwargs)

  