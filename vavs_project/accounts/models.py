# accounts.models

# DJANGO
from django.conf import settings
from django.db import models

class StaffProfile(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, unique=True)
    email_feeds = models.BooleanField(default=False)
