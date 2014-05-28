# fbdata.fbevents

# FBDATA
from .fbcomments import (
    batch_comments,
    process_comments, 
    process_comment
)
from .fbids import batch_fbids, get_fbuser_name, get_fbuser
from .fbtags import add_tagged_users, add_tagged_id
from .models import (
    FBId, 
    FBEvent
)
from .utils import (
    dict_of_objects,
    links_from_str,
    list_of_properties,
    quoted_list_str,
    timestamp_to_datetime
)

def collate_event_entries(user, start_date, end_date):
    return FBEvent.objects.filter(
                            user=user, 
                            updated_time__gte=start_date,
                            updated_time__lte=end_date)
                            
def update_events_for_user(user, graph, fbuser, start_time, end_time):
    events = get_events(user, graph, fbuser, start_time, end_time)
    levents = get_invited_events(user, graph, fbuser, start_time, end_time)
    events.extend(levents)
    batch_invitees_for_events(user, graph, events)
    return events
    
def get_events(user, graph, creator, start_time, end_time):
    query = graph.fql('SELECT eid, name, description, start_time, end_time, update_time, all_members_count, attending_count, declined_count, unsure_count FROM event WHERE creator=%s AND update_time >= %d AND update_time < %d' % (creator.user_id, start_time, end_time))
    return process_events(user, query, creator=creator)
    
def get_invited_events(user, graph, fbuser, start_time, end_time):
    query = graph.fql("SELECT eid, creator, name, description, start_time, end_time, update_time, all_members_count, attending_count, declined_count, unsure_count FROM event WHERE eid IN (SELECT eid FROM event_member WHERE uid = %s) AND update_time >= %d AND update_time < %d" % (fbuser.user_id, start_time, end_time))
    return process_events(user, query)
               
def process_events(user, query, creator=None):
    events = []
    for data in query:
        event_id = data['eid']
        event = process_event(user, event_id, data, creator=creator)
        events.append(event)
    return events
    
def process_event(user, event_id, data, creator=None):
    if not creator:
        creator = get_fbuser(data['creator'])
    updated_time = timestamp_to_datetime(data['update_time'])
    event, created = FBEvent.objects.get_or_create(
                                        user=user, 
                                        creator=creator,
                                        event_id=event_id)
    if created or event.needs_updated(updated_time):
        _update_event(event, updated_time, data)
        event.save()
    return event
    
def _update_event(event, updated_time, data):
    event.updated_time = updated_time
    event.start_time = timestamp_to_datetime(data['start_time'])
    event.end_time = timestamp_to_datetime(data['end_time'])
    name = data.get('name', None)
    if name:
        event.name = name
    description = data.get('description', None)
    if description:
        event.description = description
    event.all_members_count = data.get('all_members_count', 0)
    event.attending_count = data.get('attending_count', 0)
    event.declined_count = data.get('declined_count', 0)
    event.unsure_count = data.get('unsure_count', 0)

def batch_invitees_for_events(user, graph, events):
    event_ids_str = quoted_list_str(list_of_properties(events, 'event_id'))
    event_dict = dict_of_objects(events, 'event_id')
    query = graph.fql('SELECT eid, uid FROM event_member WHERE eid IN (%s)' % event_ids_str)
    idlist = [data['uid'] for data in query]
    fbusers = batch_fbids(idlist)
    fbuser_dict = dict_of_objects(fbusers, 'user_id')
    save_set = set()
    for data in query:
        event = event_dict[unicode(data['eid'])]
        fbuser = fbuser_dict[unicode(data['uid'])]
        event.invited.add(fbuser)
        save_set.add(event)
    for obj in save_set:
        obj.save()

