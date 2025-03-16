from django.http import HttpResponse
from django.shortcuts import render
from django.contrib import messages

from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.measure import D  # ``D`` is a shortcut for ``Distance``
from django.contrib.gis.db.models.functions import Distance

from vendor.models import Vendor

# views

def get_or_set_current_location(request):
  if 'lat' in request.session:
    lat = float(request.session.get('lat'))
    lng = float(request.session.get('lng'))
    return lng, lat
  elif 'lat' in request.GET:
    lat = float(request.GET.get('lat'))
    lng = float(request.GET.get('long'))
    request.session['lat'] = lat
    request.session['lng'] = lng
    return lng, lat
  return None

def home(request):
  vendors = Vendor.objects.filter(is_approved=True, user__is_active=True)
  location = get_or_set_current_location(request)
  if location:
    try:
      lng, lat = location
      pnt = GEOSGeometry(f"POINT({lng} {lat})", srid=4326)
      vendors = vendors.filter(
          user_profile__location__distance_lte=(pnt, D(km=100))
      ).annotate(
          distance=Distance("user_profile__location", pnt)
      ).order_by('distance')
    except:
      print(f"[WARN] Location error")

  context = {
      'vendors': vendors[:10]
  }

  return render(request, 'home.html', context)