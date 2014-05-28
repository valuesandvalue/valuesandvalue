# fbdata.utils

# PYTHON
from datetime import datetime, timedelta
import random
import re
import time

# DJANGO
from django.utils import timezone
from django.utils.text import Truncator

LONG_DATE_FORMAT = '%A %d %B %Y %I:%M:%S %p'
REGEX_URL = r'(https?://\S+)'
_FB_POST_TYPES = {
    11: 'Group created',
    12: 'Event created',
    46: 'Status update',
    56: 'Post on wall from another user',
    66: 'Note created',
    80: 'Link posted',
    128: 'Video posted',
    247: 'Photos posted',
    237: 'App story',
    257: 'Comment created',
    272: 'App story',
    285: 'Checkin to a place',
    308: 'Post in Group',
}

def fb_post_type_str(type_id, default=None):
    return _FB_POST_TYPES.get(type_id, default or type_id)
    
def links_from_str(input_str):
    return re.findall(REGEX_URL, input_str)

def wordlist_regex(words):    
    matches = '|'.join(words)
    return re.compile(r'('+matches+')', flags=re.IGNORECASE)

def make_anon_name(name):
    return ''.join([n[0] for n in name.split()]).upper()
    
def random_color():
    return "%06x" % random.randint(0,0xFFFFFF)
    
def day_range(year, month, start_day, end_day=None):
    end_day = end_day or start_day
    return (datetime(year, month, start_day, tzinfo=timezone.utc), 
            datetime(year, month, end_day, 23, 59, 59, tzinfo=timezone.utc))

def padded_date_range(start_date, end_date=None):
    end_date = end_date or start_date
    return (datetime(start_date.year, start_date.month, start_date.day, 
                tzinfo=timezone.utc),
            datetime(end_date.year, end_date.month, end_date.day, 
                23, 59, 59, tzinfo=timezone.utc))

def isodatestr_to_date(datestr):
    return isodatestr_to_datetime(datestr).date()
                
def isodatestr_to_datetime(datestr):
    return datetime.strptime(datestr, '%Y-%m-%d').replace(tzinfo=timezone.utc)
    
def date_to_timestamp(dateobj, depth=None):
    if depth:
        return int(time.mktime(dateobj.timetuple()[:depth]))
    else:
        return int(time.mktime(dateobj.timetuple()))

def ordinal_to_timestamp(ordinal):
    # 719163 == date(1970, 1, 1).toordinal()
    return (ordinal - 719163) * 24*60*60
    
def recent_time_frame(days=14):
    end = timezone.now().date() + timedelta(days=1)
    start = end - timedelta(days=days)
    return (start, end)
    
def timestamp_to_datetime(timestamp):
    return datetime.fromtimestamp(float(timestamp), timezone.utc)
 
def empty_hours():
    return [0 for i in range(24)]
 
def list_of_properties(objects, property_name):
    return [getattr(obj, property_name) for obj in objects if getattr(obj, property_name) != None]
    
def dict_of_objects(objects, property_name):
    return {unicode(getattr(obj, property_name)):obj for obj in objects}
    
def quoted_list_str(items):
    return ','.join(["'%s'" % item for item in items])
    
def property_list_str(objects, property_name):
    return ', '.join(list_of_properties(objects, property_name))
    
def get_choice_id(choicename, choices, default=0):
	for choice in choices:
		if choice[1] == choicename:
			return choice[0]
	return default
	
def get_choice_name(choice_id, choices):
	for choice in choices:
		if choice[0] == choice_id:
			return choice[1]
	return None
	
def json_error(message):
    return '{"type":"error", "message":%s}' % message
    
def can_access_user(user, username):
    return user.is_staff or user.username == username
    
def from_jstimestamp(jstimestamp):
    """Converts Javascript timestamp to datetime object."""
    return datetime.utcfromtimestamp(
                    jstimestamp / 1e3).replace(tzinfo=timezone.utc)
                    
def truncate_html(message, length=12):
    return Truncator(message).words(length, html=True, truncate=' ...')
