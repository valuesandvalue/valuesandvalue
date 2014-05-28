# fbdata.fbposts

# PYTHON
from datetime import timedelta
from dateutil import parser
import json

# FBDATA
from .fbcomments import (
    batch_comments,
    process_comments
)
from .fbids import get_fbuser
from .fbtags import (
    add_tagged_users,
    add_tagged_ids
)
from .models import (
    FBId, 
    PostComment,
    StreamPost
)
from .utils import (
    day_range,
    fb_post_type_str,
    links_from_str,
    timestamp_to_datetime
)

def collate_post_entries(user, start_date, end_date):
    return StreamPost.objects.filter(
                            user=user, 
                            created_time__gte=start_date,
                            created_time__lte=end_date)
                            
def collate_post_comments(user, start_date, end_date):
    return PostComment.objects.filter(
                            source__user=user, 
                            created_time__gte=start_date,
                            created_time__lte=end_date)

def update_posts_for_user(user, graph, fbuser, start_time, end_time):
    posts = get_stream_posts(user, graph, fbuser, start_time, end_time)
    lposts = get_liked_posts(user, graph, fbuser, start_time, end_time)
    posts.extend(lposts)
    batch_likes_for_posts(user, graph, posts)
    comments = batch_comments_for_posts(user, graph, posts)
    return (posts, comments)
    
def posts_for_day_range(year, month, start_day, end_day=None):
    start, end = day_range(year, month, start_day, end_day=end_day)
    return StreamPost.objects.filter(
                    updated_time__gte=start,
                    updated_time__lte=end)
                    
def get_stream_posts(user, graph, post_from, start_time, end_time):
    query = graph.fql('SELECT post_id, created_time, updated_time, permalink, type, message, description, share_count, like_info, comment_info, description_tags, message_tags, with_tags, tagged_ids, attachment.tagged_ids FROM stream WHERE source_id=%s AND (created_time >= %d OR updated_time >= %d) AND created_time < %d' % (post_from.user_id, start_time, start_time, end_time))
    return process_posts(user, query, post_from=post_from)

def get_liked_posts(user, graph, fbuser, start_time, end_time):
    query = graph.fql("SELECT post_id, source_id, created_time, updated_time, permalink, type, message, description, share_count, like_info, comment_info, description_tags, message_tags, with_tags, tagged_ids, attachment.tagged_ids FROM stream WHERE post_id IN (SELECT object_id FROM like WHERE user_id = %s AND object_type = 'post') AND (created_time >= %d OR updated_time >= %d) AND created_time < %d" % (fbuser.user_id, start_time, start_time, end_time))
    return process_posts(user, query)
    
def process_posts(user, query, post_from=None):
    posts = []
    for data in query:
        post_id = data['post_id']
        post = process_post(user, post_id, data, post_from=post_from)
        posts.append(post)
    return posts

def process_post(user, post_id, data, post_from=None):
    if not post_from:
        post_from = get_fbuser(data['source_id'])
    created_time = timestamp_to_datetime(data['created_time'])
    updated_time = timestamp_to_datetime(data['updated_time'])
    post, created = StreamPost.objects.get_or_create(
                                        user=user, 
                                        post_from=post_from,
                                        post_id=post_id,
                                        created_time=created_time)
    if created or post.needs_updated(updated_time):
        _update_stream_post(post, updated_time, data)
        post.save()
    return post
    
def _update_stream_post(post, updated_time, data):
    post.updated_time = updated_time
    post.post_type = data.get('type', None) or post.post_type
    permalink = data.get('permalink', None)
    if permalink:
        post.permalink = permalink
    message = data.get('message', None)
    if message:
        post.message = message
    description = data.get('description', None)
    if description:
        post.description = description
    post.share_count = data.get('share_count', 0)
    like_info = data.get('like_info', None)
    if like_info:
        post.like_count = data['like_info'].get('like_count', 0)
        post.user_likes = data['like_info'].get('user_likes', False)
    comment_info = data.get('comment_info', None)
    if comment_info:
        post.comment_count = data['comment_info'].get('comment_count', 0)
    description_tags = data.get('description_tags', None)
    if description_tags:
        for taglist in description_tags.values():
            add_tagged_users(post, taglist)
    message_tags = data.get('message_tags', None)
    if message_tags:
        for taglist in message_tags.values():
            add_tagged_users(post, taglist)
    with_tags = data.get('with_tags', None)
    if with_tags:
        add_tagged_ids(post, with_tags)
    tagged_ids = data.get('tagged_ids', None)
    if tagged_ids:
        add_tagged_ids(post, tagged_ids)
    attachment_tagged_ids = data.get('attachment.tagged_ids', None)
    if attachment_tagged_ids:
        add_tagged_ids(post, attachment_tagged_ids)

def get_comments_for_post(user, graph, post):
    comments_data = graph.fql("SELECT id, time, fromid, text, text_tags, likes, user_likes FROM comment WHERE post_id = '%s'" % post.post_id)
    process_comments(user, graph, post, comments_data, PostComment)
    
def batch_comments_for_posts(user, graph, posts):
    return batch_comments(
        user, graph, posts, PostComment, obj_id='post_id', query_id='post_id')
       
def get_likes_for_post(user, graph, post):
    likes = graph.fql("SELECT user_id FROM like WHERE post_id = '%s'" % post.post_id)
    if likes:
        for like in likes:
            fbuser, created = FBId.objects.get_or_create(user_id=like['user_id'])
            if created:
                fbuser.save()
            post.likers.add(fbuser)
        post.save()
        
def batch_likes_for_posts(user, graph, posts):
    from .fblikes import batch_likes_for_objects
    batch_likes_for_objects(user, graph, posts, obj_id='post_id', query_id='post_id')
       
def dump_post(post):
    print 'StreamPost %d' % post.id
    print 'user: %s' % post.user
    print 'post_id: %s' % post.post_id
    print 'post_from: %s' % post.post_from
    print 'permalink: %s' % post.permalink
    print 'post_type: %s' % post.post_type
    print 'post_type: %s' % fb_post_type_str(post.post_type)
    print 'created_time: %s' % post.created_time
    print 'updated_time: %s' % post.updated_time
    print 'user_likes: %s' % post.user_likes
    print 'like_count: %s' % post.like_count
    print 'comment_count: %s' % post.comment_count
    print 'share_count: %s' % post.share_count
    if post.message:
        print 'message: %s' % post.message[:64]
    else:
        print 'message: None'
    print 'description: %s' % post.description
