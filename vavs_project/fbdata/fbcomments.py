# fbdata.fbcomments

# PYTHON
import logging

# FBDATA
from .fbids import batch_fbids, get_fbuser_name
from .fbtags import add_tagged_users
from .models import (
    FBId, 
    Comment
)
from .utils import (
    dict_of_objects,
    links_from_str,
    list_of_properties,
    quoted_list_str,
    timestamp_to_datetime
)

def get_comments_for_user(user, graph, fbuser, start_time, end_time):
    comments_data = graph.fql("SELECT id, time, post_id, text, likes, user_likes FROM comment WHERE fromid = '%s' AND time >= %d AND time < %d" % (fbuser.user_id, start_time, end_time))
    print 'comments_data', comments_data
    comments = []
    for data in comments_data:
        comment, created = Comment.objects.get_or_create(
                                            post=post, comment_id=data['id'])
        if created:
            comment.fbuser = fbuser
            #comment.postid = data['post_id']
            comment.created_time = timestamp_to_datetime(data['time'])
            comment.like_count = data['likes']
            comment.user_likes = data['user_likes']
            comment.message = data.get('text', '')
            comment.save()
        comments.append(comment)
    return comments

def get_likes_for_comment(user, graph, comment): # doesn't seem to work
    likes = graph.fql("SELECT user_id FROM like WHERE object_type = 'comment' AND object_id = '%s'" % comment.comment_id)
    if likes:
        for like in likes:
            fbuser, created = FBId.objects.get_or_create(user_id=like['user_id'])
            if created:
                fbuser.save()
            if not fbuser.user_name:
                get_fbuser_name(user, graph, fbuser.user_id, fbuser=fbuser)
            comment.likers.add(fbuser)
        comment.save()
 
def get_comments_for_object(graph, object_id):
    return graph.fql("SELECT id, time, fromid, text, text_tags, likes, user_likes FROM comment WHERE object_id = '%s'" % object_id)
       
def process_comments(user, graph, fbobject, comments_data, comment_class):
    comments = []
    for data in comments_data:
        comment = process_comment(user, graph, fbobject, data, comment_class)
        comments.append(comment)
    return comments
    
def batch_comments(user, graph, fbobjects, comment_class, obj_id='object_id', 
                            query_id='object_id'):
    logger = logging.getLogger('vavs.tasks.analytics')
    object_ids_str = quoted_list_str(list_of_properties(fbobjects, obj_id))
    object_dict = dict_of_objects(fbobjects, obj_id)
    query = graph.fql("SELECT id, %s, time, fromid, text, text_tags, likes, user_likes FROM comment WHERE %s IN (%s)" % (query_id, query_id, object_ids_str))
    idlist = [data['fromid'] for data in query]
    fbusers = batch_fbids(idlist)
    fbuser_dict = dict_of_objects(fbusers, 'user_id')
    comments = []
    for data in query:
        try:
            fbobject = object_dict[unicode(data[query_id])]
        except Exception, e:
            logger.error("user: %s, query_id: %s" % (user, query_id))
            logger.error(e)
        else:
            comment = process_comment(
                        user, graph, fbobject, data, comment_class, 
                        fbusers=fbuser_dict)
            comments.append(comment)
    return comments
    
def process_comment(user, graph, fbobject, data, comment_class, fbusers=None):
    comment, created = comment_class.objects.get_or_create(
                                        source=fbobject, comment_id=data['id'])
    if created:
        if fbusers:
            fbuser = fbusers[unicode(data['fromid'])]
        else:
            fbuser, created = FBId.objects.get_or_create(user_id=data['fromid'])
            if created:
                fbuser.save()
        comment.fbuser = fbuser
        comment.created_time = timestamp_to_datetime(data['time'])
        comment.like_count = data['likes']
        comment.user_likes = data['user_likes']
        comment.message = data.get('text', '')
        text_tags = data.get('text_tags', None)
        if text_tags:
            if isinstance(text_tags, list):
                add_tagged_users(fbobject, text_tags)
            elif isinstance(text_tags, dict):
                for taglist in text_tags.values():
                    add_tagged_users(fbobject, taglist)
        comment.save()
    return comment
