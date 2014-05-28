# fbdata.details

# PYTHON
import json

# FBDATA
from .fbids import get_fbuser_from_djuser
from .generic import class_for_type
from .models import FBId
from .utils import (
    date_to_timestamp,
    json_error
)

def get_fbuser_data_json(pk, anon=True):
    try:
        fbuser = FBId.objects.get(pk=pk)
    except FBId.DoesNotExist:
        return json.dumps({'type':'error', 'message':'user not found: %s' % pk})
    return json.dumps(fbuser.detail_data(anon))
    
def get_fbobject_data_json(object_type, pk, anon=True, with_comments=True):
    if object_type == u'user':
        return get_fbuser_data_json(pk, anon=anon)
    fbobject_class = class_for_type(object_type)
    if not fbobject_class:
        return json_error("Not found: %s %s" % (object_type, pk))
    try:
        fbobject = fbobject_class.objects.get(pk=pk)
    except fbobject_class.DoesNotExist:
        return json.dumps(
            {'type':'error', 'message':'%s not found: %s' % (object_type, pk)})
    fbobject_data = fbobject.detail_data(anon)
    users = [fbobject.fb_source()]
    users.extend(fbobject.likers.all())
    users.extend(fbobject.tagged.all())
    if fbobject.user_likes:
        fbuser = get_fbuser_from_djuser(fbobject.user)
        users.append(fbuser)
        fbobject_data['likers'].append(fbuser.reference_id(anon))
    end_date = fbobject.updated_time if (
                    hasattr(fbobject, 'updated_time') and 
                    fbobject.updated_time
                ) else fbobject.created_time
    if with_comments:
        comments = fbobject.get_comments()
        comment_data = []
        for comment in comments:
            comment_data.append(comment.detail_data(anon))
            users.append(comment.fbuser)
            if comment.created_time > end_date:
                end_date = comment.created_time
        if comment_data:
            fbobject_data['comments'] = comment_data
    fbobject_data['users'] = [
        {'name':u.reference_name(anon),
        'id':u.id,
        'rgb':'#%s'%u.colour} for u in set(users)]
    fbobject_data['dates'] = {'start': fbobject.fb_timestamp(),
                'end': date_to_timestamp(end_date)}
    return json.dumps(fbobject_data)

