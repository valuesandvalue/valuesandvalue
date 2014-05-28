# fbdata.anon

# FBDATA
from .models import AnonName

def anon_name():
    return '%s %s' % tuple(AnonName.objects.all().order_by('?')[:2])
