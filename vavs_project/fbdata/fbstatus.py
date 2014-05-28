# fbdata.fbstatus

# FBDATA
from .fbcomments import (
    batch_comments,
    process_comments
)
from .fbids import get_fbuser
from .models import (
    FBStatus,
    StatusComment
)
from .utils import (
    links_from_str,
    timestamp_to_datetime
)

def collate_status_entries(user, start_date, end_date):
    return FBStatus.objects.filter(
                            user=user, 
                            created_time__gte=start_date,
                            created_time__lte=end_date)
                            
def collate_status_comments(user, start_date, end_date):
    return StatusComment.objects.filter(
                            source__user=user, 
                            created_time__gte=start_date,
                            created_time__lte=end_date)

def update_status_for_user(user, graph, fbuser, start_time, end_time):
    status_list = get_status_list(user, graph, fbuser, start_time, end_time)
    lstatus_list = get_liked_status_list(user, graph, fbuser, start_time, end_time)
    status_list.extend(lstatus_list)
    batch_likes_for_status_list(user, graph, status_list)
    comments = batch_comments_for_status_list(user, graph, status_list) 
    return (status_list, comments)
    
def get_status_list(user, graph, owner, start_time, end_time):
    query = graph.fql('SELECT status_id, time, message, like_info, comment_info FROM status WHERE uid=%s AND time >= %d AND time < %d' % (owner.user_id, start_time, end_time))
    return process_status_list(user, query, owner=owner)
    
def get_liked_status_list(user, graph, fbuser, start_time, end_time):
    query = graph.fql("SELECT status_id, uid, time, message, like_info, comment_info FROM status WHERE status_id IN (SELECT object_id FROM like WHERE user_id = %s AND object_type = 'status') AND time >= %d AND time < %d" % (fbuser.user_id, start_time, end_time))
    return process_status_list(user, query)
    
def get_status(user, graph, status_id):
    query = graph.fql('SELECT uid, time, message, like_info, comment_info FROM status WHERE status_id=%s' % status_id)
    if query:
        data = query[0]
        owner = get_fbuser(data['uid'])
        return process_status(user, status_id, data, owner=owner)
    else:
        return None
           
def process_status_list(user, query, owner=None):
    status_list = []
    for data in query:
        status_id = data['status_id']
        status = process_status(user, status_id, data, owner=owner)
        status_list.append(status)
    return status_list
    
def process_status(user, status_id, data, owner=None):
    if not owner:
        owner = get_fbuser(data['uid'])
    created_time = timestamp_to_datetime(data['time'])
    status, created = FBStatus.objects.get_or_create(
                                        user=user, 
                                        owner=owner,
                                        status_id=status_id,
                                        created_time=created_time)
    do_save = _update_status(status, data)
    if created or do_save:
        status.save()
    return status
    
def _update_status(status, data):
    do_save = False
    message = data.get('message', None)
    if message and message != status.message:
        status.message = message
        do_save = True
    like_info = data.get('like_info', None)
    if like_info:
        like_count = data['like_info'].get('like_count', 0)
        user_likes = data['like_info'].get('user_likes', False)
        if like_count != status.like_count:
            status.like_count = like_count
            do_save = True
        if user_likes != status.user_likes:
            status.user_likes = user_likes
            do_save = True
    comment_info = data.get('comment_info', None)
    if comment_info:
        comment_count = data['comment_info'].get('comment_count', 0)
        if comment_count != status.comment_count:
            status.comment_count = comment_count
            do_save = True
    return do_save
            
def get_comments_for_status(user, graph, status):
    comments_data = graph.fql("SELECT id, time, fromid, text, text_tags, likes, user_likes FROM comment WHERE object_id = '%s'" % status.status_id)
    return process_comments(user, graph, status, comments_data, StatusComment)
    
def batch_comments_for_status_list(user, graph, status_list):
    return batch_comments(user, graph, status_list, StatusComment, obj_id='status_id')
    
def get_likes_for_status(user, graph, status):
    from .fblikes import get_likes_for_object
    get_likes_for_object(user, graph, status, status.status_id)

def batch_likes_for_status_list(user, graph, status_list):
    from .fblikes import batch_likes_for_objects
    batch_likes_for_objects(user, graph, status_list, obj_id='status_id')   
         
