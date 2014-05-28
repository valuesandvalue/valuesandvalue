# fbdata.fblikes

# DJANGO
from django.conf import settings

# FBDATA
from .fbalbum import get_album
from .fbids import (
    batch_fbids, 
    friend_ids,
    get_fbuser_name
)
from .fblinks import get_link
from .fbphotos import get_photo
from .fbstatus import get_status
from .fbvideos import get_video
from .generic import (
    album_exists,
    link_exists,
    photo_exists,
    post_exists,
    status_exists,
    video_exists
)
from .models import FBId
from .utils import (
    dict_of_objects,
    list_of_properties,
    quoted_list_str
)

def update_likes_for_user(user, graph, fbuser, start_time, end_time):
    pass

#query = graph.fql("SELECT object_id, owner, caption, link FROM photo WHERE object_id IN (SELECT object_id FROM like WHERE user_id = %s AND object_type = 'photo') AND (created >= %d OR modified >= %d) AND created < %d" % (fbuser.user_id, start_time, start_time, end_time))
    
def get_likes(user, graph, fbuser, start_time, end_time):
    query = graph.fql('SELECT object_id, object_type, post_id, user_id_cursor FROM like WHERE user_id = %s' % fbuser.user_id)
    return process_likes(user, graph, fbuser, query)
    
def process_likes(user, graph, fbuser, query):
    likes = []
    for data in query:
        post_id = data.get('post_id', None)
        object_id = data.get('object_id', None)
        if post_id:
            like = process_post_like(user, graph, fbuser, post_id)
            if like:
                likes.append(like)
        elif object_id:
            object_type = data['object_type']
            like = process_object_like(user, graph, fbuser, object_id, object_type)
            if like:
                likes.append(like)
        else:
            pass
    return likes

def process_post_like(user, graph, fbuser, post_id):
    print 'process_post_like', post_id
    if post_exists(user, post_id):
        print 'post exists'
        return False
    return False
    
def process_object_like(user, graph, fbuser, object_id, object_type):
    print 'process_object_like: %s %s' % (object_id,object_type)
    if fbobject_exists(user, object_id, object_type):
        print 'object exists'
        return False
    else:
        return process_fbobject(user, graph, object_id, object_type)
   
def fbobject_exists(user, object_id, object_type):
    if object_type == 'photo':
        return photo_exists(user, object_id)
    elif object_type == 'link':
        return link_exists(user, object_id)
    elif object_type == 'video':
        return video_exists(user, object_id)
    elif object_type == 'album':
        return album_exists(user, object_id)
    elif object_type == 'status':
        return status_exists(user, object_id)
        
def process_fbobject(user, graph, object_id, object_type):
    if object_type == 'photo':
        return get_photo(user, graph, object_id)
    elif object_type == 'link':
        return get_link(user, graph, object_id)
    elif object_type == 'video':
        return get_video(user, graph, object_id)
    elif object_type == 'album':
        return get_album(user, graph, object_id)
    elif object_type == 'status':
        return get_status(user, graph, object_id)
        
def get_likes_for_object(user, graph, fbobject, fbobject_id):
    likes = graph.fql(
            "SELECT user_id FROM like WHERE object_id = '%s'" % fbobject_id)
    if likes:
        for like in likes:
            fbuser, created = FBId.objects.get_or_create(user_id=like['user_id'])
            if created:
                fbuser.save()
            if not fbuser.user_name:
                get_fbuser_name(user, graph, fbuser.user_id, fbuser=fbuser)
            fbobject.likers.add(fbuser)
        fbobject.save()
        
def batch_likes_for_objects(user, graph, fbobjects, obj_id='object_id', query_id='object_id'):
    if hasattr(settings, 'FBDATA_LIKES_LIMIT'):
        #print 'FBDATA_LIKES_LIMIT', settings.FBDATA_LIKES_LIMIT
        fbobjects_over = [obj for obj in fbobjects if obj.like_count > settings.FBDATA_LIKES_LIMIT]
        fbobjects = list(set(fbobjects) - set(fbobjects_over))
    else:
        fbobjects_over = None
    object_ids_str = quoted_list_str(list_of_properties(fbobjects, obj_id))
    object_dict = dict_of_objects(fbobjects, obj_id)
    query = graph.fql("SELECT user_id, %s FROM like WHERE %s IN (%s)" % 
                (query_id, query_id, object_ids_str))
    idlist = [data['user_id'] for data in query]
    fbusers = batch_fbids(idlist)
    fbuser_dict = dict_of_objects(fbusers, 'user_id')
    save_set = set()
    for data in query:
        fbobject = object_dict[unicode(data[query_id])]
        fbuser = fbuser_dict[unicode(data['user_id'])]
        fbobject.likers.add(fbuser)
        save_set.add(fbobject)
        #fbuser.users.add(user) # maybe use later?
        #save_set.add(fbuser)
    for obj in save_set:
        obj.save()
    if fbobjects_over:
        batch_friend_likes_for_objects(
                user, graph, fbobjects_over, obj_id=obj_id, query_id=query_id)
        
def batch_friend_likes_for_objects(user, graph, fbobjects, obj_id='object_id', query_id='object_id'):
    object_ids_str = quoted_list_str(list_of_properties(fbobjects, obj_id))
    object_dict = dict_of_objects(fbobjects, obj_id)
    friend_ids_str = quoted_list_str(friend_ids(user))
    query = graph.fql("SELECT user_id, %s FROM like WHERE %s IN (%s) AND user_id IN (%s)" % 
                (query_id, query_id, object_ids_str, friend_ids_str))
    idlist = [data['user_id'] for data in query]
    #print 'batch_friend', idlist
    fbusers = batch_fbids(idlist)
    fbuser_dict = dict_of_objects(fbusers, 'user_id')
    save_set = set()
    for data in query:
        fbobject = object_dict[unicode(data[query_id])]
        fbuser = fbuser_dict[unicode(data['user_id'])]
        fbobject.likers.add(fbuser)
        save_set.add(fbobject)
        #fbuser.users.add(user) # maybe use later?
        #save_set.add(fbuser)
    for obj in save_set:
        obj.save()

def process_like(user, graph, fbobject, data, save=True):
    fbuser, created = FBId.objects.get_or_create(user_id=data['user_id'])
    if created:
        fbuser.save()
    fbobject.likers.add(fbuser)
    if save:
        fbobject.save()
