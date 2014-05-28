# addata.activity

# PYTHON
from datetime import timedelta
import json

# QSSTATS
from qsstats import QuerySetStats

# FBDATA
from fbdata.fbids import get_fbuser_from_djuser
from fbdata.utils import (
    date_to_timestamp,
    padded_date_range
)

# ADDATA
from .models import (
    AdHourlyActivity,
    AdRecord,
    FBAd,
    FBSponsored
)

def get_hourly_activity(user, date, hour):
    activity, created = AdHourlyActivity.objects.get_or_create(user=user,
                                              date=date,
                                              hour=hour)
    return activity

def get_activity_for_day(user, date):
    return AdHourlyActivity.objects.filter(user=user, date=date)

def get_activity_for_period(user, start_date, end_date):
    return AdHourlyActivity.objects.filter(user=user, 
                                            date__gte=start_date, 
                                            date__lte=end_date)
                                                    
def process_hourly_activity(user, start, end, modelclass):
    if modelclass == AdRecord:
        qs = modelclass.objects.filter(_user_id=user.id, date__range=(start, end))
    else:
        qs = modelclass.objects.filter(user=user, date__range=(start, end))
    if not qs:
        return {}
    qss = QuerySetStats(qs, 'date')
    start_date = start.date()
    end_date = end.date()
    if start_date == end_date:
        end_date = start_date + timedelta(days=1)
    timeseries = qss.time_series(
                        start_date, end=end_date, interval='hours', date_field='date')
    activities = {}
    for t in timeseries:
        if t[1]:
            d = t[0]
            activity = get_hourly_activity(user, start_date, d.hour)
            if modelclass == AdRecord:
                for r in qs.filter(date__hour=d.hour):
                    activity.adrecords.add(r)
            elif modelclass == FBSponsored:
                for r in qs.filter(date__hour=d.hour):
                    activity.fbsponsored.add(r)
            elif modelclass == FBAd:
                for r in qs.filter(date__hour=d.hour):
                    activity.fbads.add(r)
            activity.adtotal = activity.adrecords.count()
            activity.fbadtotal = activity.fbads.count()
            activity.fbsptotal = activity.fbsponsored.count()
            activity.save()
            activities[d] = activity    
    return activities

def process_all_hourly_activity(user, start, end):
    ad_activities = process_hourly_activity(user, start, end, AdRecord)
    fbsp_activities = process_hourly_activity(user, start, end, FBSponsored)
    fbad_activities = process_hourly_activity(user, start, end, FBAd)
    return {'ad_activities': ad_activities, 
            'fbsp_activities': fbsp_activities,
            'fbad_activities': fbad_activities}

def process_activity_range(user, start_date, end_date):
    diff = end_date - start_date
    for i in range(diff.days):
        day = start_date + timedelta(days=i)
        start, end = padded_date_range(day)
        process_all_hourly_activity(user, start, end)

def activity_data_json(user, start_date, end_date, fbuser=None, anon=True):
    data = get_activity_for_period(user, start_date, end_date)
    jdata = {'dates': {'start': date_to_timestamp(start_date),
                    'end': date_to_timestamp(end_date)},
            'activity': [a.packed_data() for a in data]}
    return json.dumps(jdata)
