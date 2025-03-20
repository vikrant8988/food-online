from django.db import models
from accounts.models import User, UserProfile
from accounts.utils import send_notification
from datetime import datetime, time

# Create your models here.
class Vendor(models.Model):
  user = models.OneToOneField(
    User,
    related_name="user",
    on_delete=models.CASCADE,
    limit_choices_to={'role': User.VENDOR}  # Restrict choices at the database level
    )
  user_profile = models.OneToOneField(UserProfile, related_name="userprofile", on_delete=models.CASCADE)
  vendor_name = models.CharField(max_length=50)
  slug = models.SlugField(max_length=100, unique=True)
  vendor_license = models.ImageField(upload_to="vendor/license")
  is_approved = models.BooleanField(default=False)
  created_at = models.DateTimeField(auto_now_add=True)
  modified_at = models.DateTimeField(auto_now=True)
  
  def __str__(self):
    return self.vendor_name
  
  def is_open(self):
    today_day = datetime.today().isoweekday()  # Monday=1 ... Sunday=7
    today_business_hour = OpeningHour.objects.filter(vendor=self, day=today_day).first()
    current_time = datetime.now().time()
    isOpen = False
    
    if today_business_hour and not today_business_hour.is_closed:
      from_hour = datetime.strptime(today_business_hour.from_hour, "%I:%M %p").time()
      to_hour = datetime.strptime(today_business_hour.to_hour, "%I:%M %p").time()
      isOpen = current_time >= from_hour and current_time <= to_hour
      
    return isOpen
    

  def save(self, *args, **kwargs):
    if self.pk is not None:
      orig = Vendor.objects.get(pk = self.pk)
      if self.is_approved != orig.is_approved:
        mail_template = "accounts/emails/admin_approval_email.html"
        context = {
          'user' : self.user,
          'is_approved' : self.is_approved
        }
        if self.is_approved:
          mail_subject = "Marketplace Menu: Approved"
        else:
          mail_subject = "Marketplace Menu: Ineligible" 
        send_notification(mail_subject, mail_template, context)
        
    return super(Vendor, self).save(*args, **kwargs)
  

  
class OpeningHour(models.Model):
  DAYS = [
    (1, ("Monday")),
    (2, ("Tuesday")),
    (3, ("Wednesday")),
    (4, ("Thursday")),
    (5, ("Friday")),
    (6, ("Saturday")),
    (7, ("Sunday")),
  ]
  
  HOURS_OF_DAY_24 = [(time(h,m).strftime('%I:%M %p'),time(h,m).strftime('%I:%M %p')) for h in range(0,24) for m in (0,30)]
  
  vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
  day =  models.IntegerField(choices=DAYS)
  from_hour = models.CharField(choices=HOURS_OF_DAY_24, max_length=10, blank=True)
  to_hour = models.CharField(choices=HOURS_OF_DAY_24, max_length=10, blank=True)
  is_closed = models.BooleanField(default=False)
  
  class Meta:
    ordering = ('day', '-from_hour')
    unique_together = ('vendor','day')
    
  def __str__(self):
    return self.get_day_display()
  