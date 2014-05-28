# addata.handlers

# ADDATA
from .models import (
    AdRecord,
    FBAd,
    FBSponsored
)

_AD_CLASSES = {
    'ad': AdRecord,
    'fbad': FBAd,
    'fbsp': FBSponsored,
}
def ad_class_for_type(object_type):
    return _AD_CLASSES.get(object_type, None)

def get_user_ads(user, start_date, end_date):
    return AdRecord.objects.filter(_user_id=user.id, 
                date__gte=start_date, date__lte=end_date)
                
def get_user_fbads(user, start_date, end_date):
    return FBAd.objects.filter(user=user, 
                date__gte=start_date, date__lte=end_date)
                
def get_user_fbsponsored(user, start_date, end_date):
    return FBSponsored.objects.filter(user=user, 
                date__gte=start_date, date__lte=end_date)


_data_handlers = {
    'ads': get_user_ads,
    'fbads': get_user_fbads,
    'fbsponsored': get_user_fbsponsored
}

def get_user_data(user, datatype, start_date, end_date):
    data = {}
    if datatype == 'all':
        data['ads'] = get_user_ads(user, start_date, end_date)
        data['fbads'] = get_user_fbads(user, start_date, end_date)
        data['fbsps'] = get_user_fbsponsored(user, start_date, end_date)
    else:
        func = _data_handlers.get(datatype, None)
        if func:
            data[datatype] = func(user, start_date, end_date)
    return data
    
def get_all_user_data(user):
    data = {}
    data['ads'] = AdRecord.objects.filter(_user_id=user.id)
    data['fbads'] = FBAd.objects.filter(user=user)
    data['fbsps'] = FBSponsored.objects.filter(user=user)
    return data
 
