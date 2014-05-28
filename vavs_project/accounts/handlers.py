# accounts.handlers

# DJANGO
from django.core.exceptions import PermissionDenied

# ACCOUNTS
from .models import StaffProfile

def get_staff_profile(user):
    if user.is_staff:
        profile, created = StaffProfile.objects.get_or_create(user=user)
        if created:
            profile.save()
        return profile
    else:
        raise PermissionDenied("User is not staff")
        
def get_emails_for_feeds():
    return StaffProfile.objects.filter(
                        email_feeds=True).values_list('user__email', flat=True)
   
