
def detectUser(user):
  if user.role == 1:
    redirectUrl = "vendorDashboard"
    return redirectUrl
  if user.role == 2:
    redirectUrl = "customerDashboard"
    return redirectUrl
  elif user.role is None and user.is_super_admin:
    redirectUrl = "admin"
    return redirectUrl
    
  