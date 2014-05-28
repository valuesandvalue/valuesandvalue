# addata.details

# PYTHON
from datetime import timedelta
import json

# DJANGO
from django.db.models import Q

# FBDATA
from fbdata.utils import (
    date_to_timestamp,
    json_error,
    padded_date_range
)

# ADDATA
from .handlers import ad_class_for_type
from .models import AdRecord

def get_ad_data_json(ad_type, pk, anon=True):
    adobject_class = ad_class_for_type(ad_type)
    if not adobject_class:
        return json_error("Not found: %s %s" % (ad_type, pk))
    try:
        adobject = adobject_class.objects.get(pk=pk)
    except adobject_class.DoesNotExist:
        return json.dumps(
            {'type':'error', 'message':'%s not found: %s' % (ad_type, pk)})
    adobject_data = adobject.detail_data(anon=anon)
    return json.dumps(adobject_data)
    
def ad_domain_data_for_period(user, start_time, end_time, anon=True):
    ads = AdRecord.objects.filter(~Q(_ref_domain_id=0), ~Q(_domain_id=0),
                                    _user_id=user.id,
                                    date__range=(start_time, end_time))
    data = {}
    refs = set()
    for ad in ads:
        domain = ad.get_domain().name
        ref = ad.get_ref_domain().ref_name(anon=anon)
        refs.add(ref)
        if not data.has_key(domain):
            data[domain] = {}
        if not data[domain].has_key(ref):
            data[domain][ref] = 1
        else:
            data[domain][ref] += 1
    ad_data = {}
    for domain, values in data.items():
        reflist = []
        for ref, count in values.items():
            reflist.append([ref, count])
        ad_data[domain] = reflist
    return {'ads': ad_data, 'refs':list(refs)}
    
def ad_details_json(user, start_time, end_time, anon=True):
    ad_data = ad_domain_data_for_period(user, start_time, end_time, anon=anon)
    if ad_data:
        ad_data['dates'] = {'start': date_to_timestamp(start_time),
                            'end': date_to_timestamp(end_time)}
        return json.dumps(ad_data)
    else:
        return json_error('No data for period: %s %s' % (start_time, end_time))

def ad_details_for_hour_json(user, hour, anon=True):
    start_time = hour
    end_time = hour + timedelta(hours=1)
    ad_data = ad_domain_data_for_period(user, start_time, end_time, anon=anon)
    if ad_data:
        ad_data['dates'] = {'start': date_to_timestamp(start_time),
                            'end': date_to_timestamp(end_time)}
        ad_data['hour'] = date_to_timestamp(hour)
        return json.dumps(ad_data)
    else:
        return json_error('No data for period: %s %s' % (start_time, end_time))       
