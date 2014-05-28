# fbdata.handlers

# PYTHON
from datetime import timedelta
from dateutil import parser
import json

# DJNAGO
from django.db.models import Q

# DJANGO FACEBOOK
from django_facebook.models import FacebookUser, FacebookLike

# FBDATA
from .fbids import (
    get_facebook_graph,
    get_fbuser_from_djuser
)
from .fbphotos import update_photos_for_user
from .fbposts import update_posts_for_user
from .models import (
    Comment,
    PhotoComment,
    PostComment,
    #CoOccurrence,
    DailyStreamActivity,
    FBId, 
    FBPhoto,
    #FeedPost, 
    #FriendFeedActivity,
    #FriendSet,
    #Like,
    StreamPost
)
from .utils import (
    date_to_timestamp,
    day_range,
    empty_hours,
    #fb_post_type_str,
    links_from_str,
    ordinal_to_timestamp,
    recent_time_frame,
    timestamp_to_datetime
)

# for tests
global user, graph, fbuser
global start_date, end_date
global start_time, end_time
    
def test(username='simonyuilldev', start=None, end=None):
    from django.contrib.auth.models import User
    from datetime import date
    global user, graph, fbuser
    global start_date, end_date
    global start_time, end_time
    user = User.objects.get(username=username)
    graph = get_facebook_graph(user)
    fbuser = get_fbuser_from_djuser(user)
    start = start or (2013, 12, 1)
    end = end or (2013, 12, 30)
    start_date = date(*start)
    end_date =  date(*end)
    start_time = int(date_to_timestamp(start_date))
    end_time = int(date_to_timestamp(end_date))
    
def test_ks():
    test(username='kirstystansfield18')
    
def testdates():
    from datetime import date
    start_date = date(2013, 12, 1)
    end_date = date(2013, 12, 30)
    return (start_date, end_date)

def clean():
    FBId.objects.all().delete()
    FBPhoto.objects.all().delete()
    FBVideo.objects.all().delete()
    FBLink.objects.all().delete()
    FBStatus.objects.all().delete()
    FBAlbum.objects.all().delete()
    StreamPost.objects.all().delete()
    PostComment.objects.all().delete()
    PhotoComment.objects.all().delete()
    VideoComment.objects.all().delete()
    LinkComment.objects.all().delete()
    StatusComment.objects.all().delete()
    AlbumComment.objects.all().delete()
    AdTopic.objects.all().delete()
    UserAnalysis.objects.all().delete()
    DailyStreamActivity.objects.all().delete()
        
def run(user, graph, start_date, end_date):
    posts = update_stream(user, graph, start_date, end_date)
    #process_daily_activity_range(user, start_date, end_date)
    return posts
    
def update_stream(user, graph, start_date, end_date):
    start_time = int(date_to_timestamp(start_date))
    end_time = int(date_to_timestamp(end_date))
    # user's posts
    fbuser = get_fbuser_from_djuser(user)
    posts = update_posts_for_user(user, graph, fbuser, start_time, end_time)
#    print posts
#    # friends
#    friends = FBId.objects.filter(users=user)[:10]
#    for fbuser in friends:
#        source_id = fbuser.user_id
#        fbposts = update_posts_for_source(
#                            user, graph, source_id, start_time, end_time)
#        posts.extend(fbposts)
#        print fbposts
    return posts
    
def update_photos(user, graph, start_date, end_date):
    start_time = int(date_to_timestamp(start_date))
    end_time = int(date_to_timestamp(end_date))
    # user's posts
    fbuser = get_fbuser_from_djuser(user)
    photos = update_photos_for_user(user, graph, fbuser, start_time, end_time)
    return photos
    
#def update_posts_for_source(user, graph, source_id, start_time, end_time):
#    posts = get_stream_posts(user, graph, source_id, start_time, end_time)
#    for post in posts:
#        get_likes_for_post(user, graph, post)
#        get_comments_for_post(user, graph, post)
#    return posts

#def get_facebook_graph(user):
#    profile = user.get_profile()
#    return profile.get_offline_graph()
#    
#def get_related_fbuser(user, other_id, other_name):
#    try:
#       return FacebookUser.objects.get(user_id=user.id, facebook_id=other_id)
#    except FacebookUser.DoesNotExist:
#        return FacebookUser.objects.create(
#                user_id=UNCONNECTED, 
#                facebook_id=other_id,
#                name=other_name)
# 
#def get_fbuser(user_id, user_name, fb_type=None):
#    fbuser, do_save = FBId.objects.get_or_create(user_id=user_id)
#    if user_name and fbuser.user_name != user_name:
#        fbuser.user_name = user_name
#        do_save = True
#    if fb_type and fbuser.fb_type != fb_type:
#        fbuser.fb_type = fb_type
#        do_save = True
#    if do_save:
#        fbuser.save()
#    return fbuser

#def get_fbuser_from_djuser(user):
#    profile = user.get_profile()
#    return get_fbuser(profile.facebook_id, profile.facebook_name)

#def _connection_to_fbuser(user, connection):
#    fb_id = connection['target_id']
#    try:
#        friend = FacebookUser.objects.get(user_id=user.id, facebook_id=fb_id)
#    except FacebookUser.DoesNotExist:
#        friend = None
#    if not friend:
#        try:
#            friend = FacebookLike.objects.get(user_id=user.id, facebook_id=fb_id)
#        except FacebookLike.DoesNotExist:
#            friend = None
#    fbuser, do_save = FBId.objects.get_or_create(user_id=fb_id)
#    if friend:
#        if not fbuser.user_name:
#            fbuser.user_name = friend.name
#            do_save = True
#    if not fbuser.fb_type:
#        fbuser.fb_type = connection['target_type']
#        do_save = True
#    if not fbuser.has_user(user):
#        fbuser.users.add(user)
#        do_save = True
#    if do_save:
#        fbuser.save()
#    return fbuser
#        
#def get_connections(user, graph):
#    connections = graph.fql('SELECT target_id, target_type FROM connection WHERE source_id = me()')
#    fbusers = []
#    for connection in connections:
#        fbusers.append(_connection_to_fbuser(user, connection))
#    return fbusers
    
#def get_stream_posts(user, graph, source_id, start_time, end_time):
#    stream = graph.fql('SELECT post_id, created_time, updated_time, permalink, type, message, description, share_count, like_info, comment_info, description_tags, message_tags, with_tags, tagged_ids, attachment.tagged_ids FROM stream WHERE source_id=%s AND (created_time >= %d OR updated_time >= %d) AND created_time < %d' % (source_id, start_time, start_time, end_time))
#    posts = []
#    post_from, created = FBId.objects.get_or_create(user_id=source_id)
#    if created:
#        post_from.save()
#    if not post_from.user_name:
#        get_fbuser_name(user, graph, post_from.user_id, fbuser=post_from)
#    for data in stream:
#        post_id = data['post_id']
#        created_time = timestamp_to_datetime(data['created_time'])
#        updated_time = timestamp_to_datetime(data['updated_time'])
#        post, created = StreamPost.objects.get_or_create(
#                                            user=user, 
#                                            post_from=post_from,
#                                            post_id=post_id,
#                                            created_time=created_time)
#        if created or post.needs_updated(updated_time):
#            _update_stream_post(post, updated_time, data)
#            post.save()
#        posts.append(post)
#    return posts


    
#'SELECT text FROM comment WHERE post_id IN (SELECT post_id FROM stream WHERE source_id IN (SELECT uid1 FROM friend WHERE uid2=me()) AND comment_info.comment_count > 0 AND created_time >= %d AND created_time < %d)' % (start_time, end_time)

#q = graph.fql('SELECT text FROM comment WHERE post_id IN (SELECT post_id FROM stream WHERE source_id in (SELECT uid1 FROM friend WHERE uid2=me()) AND comment_info.comment_count > 0 AND (created_time >= %d OR updated_time >= %d) AND created_time < %d)' % (start_time, start_time, end_time))

#graph.fql('SELECT object_id FROM like WHERE user_id = me()')

#graph.fql('SELECT post_id, created_time, attachment.href FROM stream WHERE source_id = 702381566 AND created_time >= %d AND created_time <= %d' % (start_time, end_time))

#def _update_stream_post(post, updated_time, data):
#    post.updated_time = updated_time
#    post.post_type = data.get('type', None) or post.post_type
#    permalink = data.get('permalink', None)
#    if permalink:
#        post.permalink = permalink
#    message = data.get('message', None)
#    if message:
#        post.message = message
#    description = data.get('description', None)
#    if description:
#        post.description = description
#    post.share_count = data.get('share_count', 0)
#    like_info = data.get('like_info', None)
#    if like_info:
#        post.like_count = data['like_info'].get('like_count', 0)
#        post.user_likes = data['like_info'].get('user_likes', False)
#    comment_info = data.get('comment_info', None)
#    if comment_info:
#        post.comment_count = data['comment_info'].get('comment_count', 0)
#    description_tags = data.get('description_tags', None)
#    if description_tags:
#        print 'description_tags', description_tags
#        for taglist in description_tags.values():
#            _add_tagged_users(post, taglist)
#    message_tags = data.get('message_tags', None)
#    if message_tags:
#        print 'message_tags', message_tags
#        for taglist in message_tags.values():
#            _add_tagged_users(post, taglist)
#    with_tags = data.get('with_tags', None)
#    if with_tags:
#        print 'with_tags', with_tags
#        _add_tagged_ids(post, with_tags)
#    tagged_ids = data.get('tagged_ids', None)
#    if tagged_ids:
#        print 'tagged_ids', tagged_ids
#        _add_tagged_ids(post, tagged_ids)
#    attachment_tagged_ids = data.get('attachment.tagged_ids', None)
#    if attachment_tagged_ids:
#        print 'attachment.tagged_ids', attachment_tagged_ids
#        _add_tagged_ids(post, attachment_tagged_ids)
    
#def _add_tagged_users(post, taglist):
#    for tag in taglist:
#        user_id = tag['id']
#        user_name = tag['name']
#        fb_type = tag['type']
#        fbuser = get_fbuser(user_id, user_name, fb_type=fb_type)
#        post.tagged.add(fbuser)
#        
#def _add_tagged_ids(post, taglist):
#    for user_id in taglist:
#        fbuser, created = FBId.objects.get_or_create(user_id=user_id)
#        if created:
#            fbuser.save()
#        post.tagged.add(fbuser)

#def dump_post(post):
#    print 'StreamPost %d' % post.id
#    print 'user: %s' % post.user
#    print 'post_id: %s' % post.post_id
#    print 'post_from: %s' % post.post_from
#    print 'permalink: %s' % post.permalink
#    print 'post_type: %s' % post.post_type
#    print 'post_type: %s' % fb_post_type_str(post.post_type)
#    print 'created_time: %s' % post.created_time
#    print 'updated_time: %s' % post.updated_time
#    print 'user_likes: %s' % post.user_likes
#    print 'like_count: %s' % post.like_count
#    print 'comment_count: %s' % post.comment_count
#    print 'share_count: %s' % post.share_count
#    if post.message:
#        print 'message: %s' % post.message[:64]
#    else:
#        print 'message: None'
#    print 'description: %s' % post.description
          
#def get_likes_for_post(user, graph, post):
#    likes = graph.fql("SELECT user_id FROM like WHERE post_id = '%s'" % post.post_id)
#    if likes:
#        for like in likes:
#            fbuser, created = FBId.objects.get_or_create(user_id=like['user_id'])
#            if created:
#                fbuser.save()
#            if not fbuser.user_name:
#                get_fbuser_name(user, graph, fbuser.user_id, fbuser=fbuser)
#            post.likers.add(fbuser)
#        post.save()
#        
#def get_comments_for_post(user, graph, post):
#    comments_data = graph.fql("SELECT id, time, fromid, text, likes, user_likes FROM comment WHERE post_id = '%s'" % post.post_id)
#    comments = []
#    for data in comments_data:
#        comment, created = Comment.objects.get_or_create(post=post, comment_id=data['id'])
#        if created:
#            fbuser, created = FBId.objects.get_or_create(user_id=data['fromid'])
#            if created:
#                fbuser.save()
#            if not fbuser.user_name:
#                get_fbuser_name(user, graph, fbuser.user_id, fbuser=fbuser)
#            comment.fbuser = fbuser
#            comment.created_time = timestamp_to_datetime(data['time'])
#            comment.like_count = data['likes']
#            comment.user_likes = data['user_likes']
#            comment.message = data.get('text', '')
#            comment.save()
#        comments.append(comment)
#    return comments
    
#def get_comments_for_user(user, graph, fbuser, start_time, end_time):
#    comments_data = graph.fql("SELECT id, time, post_id, text, likes, user_likes FROM comment WHERE fromid = '%s' AND time >= %d AND time < %d" % (fbuser.user_id, start_time, end_time))
#    print 'comments_data', comments_data
#    comments = []
#    for data in comments_data:
#        comment, created = Comment.objects.get_or_create(post=post, comment_id=data['id'])
#        if created:
#            comment.fbuser = fbuser
#            comment.postid = data['post_id']
#            comment.created_time = timestamp_to_datetime(data['time'])
#            comment.like_count = data['likes']
#            comment.user_likes = data['user_likes']
#            comment.message = data.get('text', '')
#            comment.save()
#        comments.append(comment)
#    return comments

#def get_likes_for_comment(user, graph, comment): # doesn't seem to work
#    likes = graph.fql("SELECT user_id FROM like WHERE object_type = 'comment' AND object_id = '%s'" % comment.comment_id)
#    if likes:
#        for like in likes:
#            fbuser, created = FBId.objects.get_or_create(user_id=like['user_id'])
#            if created:
#                fbuser.save()
#            if not fbuser.user_name:
#                get_fbuser_name(user, graph, fbuser.user_id, fbuser=fbuser)
#            comment.likers.add(fbuser)
#        comment.save()
        
#def get_fbuser_name(user, graph, user_id, fbuser=None):
##    try:
##        user_data = graph.fql('SELECT name FROM user WHERE uid = %s' % user_id)
##    except:
##        user_data = graph.fql('SELECT name FROM page WHERE page_id = %s' % user_id)
##    print 'user_data', user_data
#    if not fbuser:
#        fbuser, created = FBId.objects.get_or_create(user_id=user_id)
#    #fbuser.user_name = user_data[0]['name']
#    fbuser.users.add(user)
#    fbuser.save()
#    return fbuser
    
#def posts_for_day_range(year, month, start_day, end_day=None):
#    start, end = day_range(year, month, start_day, end_day=end_day)
#    return StreamPost.objects.filter(
#                    updated_time__gte=start,
#                    updated_time__lte=end)

#def narrative_data(user, start, end):
#    posts = StreamPost.objects.filter(
#                            user=user,
#                            created_time__gte=start, 
#                            created_time__lte=end).order_by('created_time')
#    photos = FBPhoto.objects.filter(
#                            user=user,
#                            created_time__gte=start, 
#                            created_time__lte=end).order_by('created_time')
#    post_data = []
#    user_fb = get_fbuser_from_djuser(user)
#    friend_list = [user_fb]
#    for post in posts:
#        friends = set(post.likers.all())
#        for fbuser in post.tagged.all():
#            friends.add(fbuser)
##        comment_friends = set(
##                FBId.objects.filter(comment__post=post).distinct('id'))
#        comments = PostComment.objects.filter(source=post)
#        comments_data = {}
#        for cm in comments:
#            friends.add(cm.fbuser)
#            user_id = cm.fbuser.user_id
#            comments_data[user_id] = comments_data.get(
#                                                 user_id, 0) + len(cm.message)
#        if post.post_from:
#            friends.add(post.post_from)
#        if post.user_likes:
#            friends.add(user_fb)
#        friend_list.extend(friends)
#        post_data.append({'date': date_to_timestamp(post.created_time),
#                'pk': post.id,
#                'type': post.post_type,
#                'id': post.post_id,
#                'from': post.post_from.user_id,
#                'info': post.display_info(),
#                'users':[f.user_id for f in friends],
#                'comments':comments_data})
#    for photo in photos:
#        friends = set(photo.likers.all())
#        for fbuser in photo.tagged.all():
#            friends.add(fbuser)
#        comments = PhotoComment.objects.filter(source=photo)
#        comments_data = {}
#        for cm in comments:
#            friends.add(cm.fbuser)
#            user_id = cm.fbuser.user_id
#            comments_data[user_id] = comments_data.get(
#                                                 user_id, 0) + len(cm.message)
#        if photo.owner:
#            friends.add(photo.owner)
#        if photo.user_likes:
#            friends.add(photo.owner)
#        friend_list.extend(friends)
#        post_data.append({'date': date_to_timestamp(photo.created_time),
#                'pk': photo.id,
#                'type': 'photo',
#                'id': photo.object_id,
#                'from': photo.owner.user_id,
#                'info': photo.display_info(),
#                'users':[f.user_id for f in friends],
#                'comments':comments_data})
#    user_data = [
#        {'name':f.reference_name(),
#        'pk':f.id,
#        'id':f.user_id, 
#        'rgb':'#%s'%f.colour} for f in set(friend_list)]
#    return (post_data, user_data)
     
#def narrative_data_json(user, start, end):
#    fbuser = get_fbuser_from_djuser(user)
#    post_data, user_data = narrative_data(user, start, end)
#    return json.dumps({
#        'source': fbuser.reference_name(),
#        'source_pk': fbuser.pk,
#        'dates': {'start': date_to_timestamp(start),
#                'end': date_to_timestamp(end)},
#        'users': user_data,
#        'posts': post_data})

def process_daily_activity(user, date):
    start, end = day_range(date.year, date.month, date.day)
    posts = StreamPost.objects.filter(user=user,
                    updated_time__gte=start,
                    created_time__lte=end)
    comments = Comment.objects.filter(post__user=user,
                    created_time__gte=start,
                    created_time__lte=end)
    if not posts and not comments:
        return
    activity, created = DailyStreamActivity.objects.get_or_create(
                                    user=user, date=date)
    if not created:
        activity.hourly = empty_hours()
    for post in posts:
        print 'post', post.id
        activity.posts.add(post)
        if post.message:
            message_length = len(post.message)
            activity.chars += message_length
            print 'message_length', message_length
        else:
            message_length = 0
        if post.post_from:
            activity.fbusers.add(post.post_from)
#            friend_activity = _make_friend_activity(user, post.post_from, date)
#            friend_activity.posts.add(post)
#            friend_activity.chars += message_length
#            friend_activity.save()
#            print 'friend_activity.chars', friend_activity.chars
        activity.likes += post.like_count
        activity.shares += post.share_count
        post_hour = post.get_reference_hour()
        post_activity = post.like_count
        post_activity += post.share_count
        activity.hourly[post_hour] += post_activity
        activity.comments += post.comment_count
        #print 'activity.comments', activity.comments
    for comment in comments:
        comment_hour = comment.get_reference_hour()
        activity.hourly[comment_hour] += 1
        comment_length = len(comment.message)
        c_likes = comment.like_count + int(comment.user_likes)
        activity.likes += c_likes
        activity.hourly[comment_hour] += c_likes
        activity.chars += comment_length
        activity.fbusers.add(comment.fbuser)
    activity.save()
    return activity

def process_daily_activity_range(user, start, end):
    pdate = start
    while pdate <= end:
        process_daily_activity(user, pdate)
        pdate += timedelta(days=1)
    
def daily_activity_data(user, start, end): # include hourly
    # date, value, pk, hourly
    activity_period = DailyStreamActivity.objects.filter(user=user,
                        date__gte=start, date__lte=end).order_by('date')
    activity_data = []
    model_data = {}
    ord_date = start.toordinal()
    prev = ord_date-1
    for daily_activity in activity_period:
        ord_date = daily_activity.date.toordinal()
        gap = ord_date-prev
        if gap > 1:
            tmp_date = prev+1
            activity_data.append({'x':ordinal_to_timestamp(tmp_date), 'y':0})
        if gap > 2:
            tmp_date = ord_date-1
            activity_data.append({'x':ordinal_to_timestamp(tmp_date), 'y':0})
        timestamp = ordinal_to_timestamp(ord_date)
        activity_data.append(
            {'x':timestamp,
            'y':daily_activity.posts.count()})
        model_data[timestamp] = daily_activity.id
        prev = ord_date
    end_ord = end.toordinal()
    gap = end_ord - ord_date
    if gap > 0:
        activity_data.append({'x':ordinal_to_timestamp(ord_date+1), 'y':0})
    if gap > 1:
        activity_data.append({'x':ordinal_to_timestamp(end_ord), 'y':0})
    return (activity_data, model_data)

def analysis_data_json(user, start, end):
    fbuser = get_fbuser_from_djuser(user)
    post_data, user_data = narrative_data(user, start, end)
    activity_data, model_data = daily_activity_data(user, start, end)
    return json.dumps({
        'source': fbuser.anon_name,
        'source_pk': fbuser.pk,
        'dates': {'start': date_to_timestamp(start),
                'end': date_to_timestamp(end)},
        'users': user_data,
        'posts': post_data,
        'activity': activity_data})

                                
####################################################
# OLD STUFF
####################################################
#def get_feed(user, graph):
#    # NOTE: add paging
#    query = graph.get('me/feed')
#    data = query.get('data', [])
#    for post in data:
#        post_id = post['id']
#        if post.has_key('from'):
#            fbuser = get_fbuser(int(post['from']['id']), post['from']['name'])
#        else:
#            fbuser = None
#        fp, created = FeedPost.objects.get_or_create(
#                                user=user, 
#                                post_from=fbuser,
#                                post_id=post_id)
#        if created:
#            print 'NEW FeedPost'
#            fp.post_type = post['type']
#            fp.status_type = post.get('status_type', '')
#            fp.created_time = parser.parse(post['created_time'])
#            fp.save()
#            ut_str = post.get('updated_time', None)
#            if ut_str:
#                updated_time = parser.parse(ut_str)
#            else:
#                updated_time = None
#            _update_post(user, fp, post, updated_time)
#            fp.save()
#        else:
#            print 'OLD FeedPost'
#            ut_str = post.get('updated_time', None)
#            if ut_str:
#                updated_time = parser.parse(ut_str)
#                print 'updated_time', updated_time
#                if not fp.updated_time or fp.updated_time < updated_time:
#                    print 'UPDATED FeedPost'
#                    _update_post(user, fp, post, updated_time)
#                    fp.save()

#def _update_post(user, fp, post, updated_time):
#    fp.updated_time = updated_time
#    message = post.get('message', None)
#    if message:
#        fp.message = message
#    likes = post.get('likes', None)
#    if likes:
#        process_likes(user, fp, likes)
#    shares = post.get('shares', None)
#    if shares:
#        process_shares(user, fp, shares)
#    comments = post.get('comments', None)
#    if comments:
#        process_comments(user, fp, comments)
#    fp.raw_data = json.dumps(post)
#    
#def process_likes(user, fp, likes):
#    fp.like_count = likes.get('count', 0)
#    data = likes.get('data', [])
#    for item in data:
#        fbuser = get_fbuser(int(item['id']), item['name'])
#        like, created = Like.objects.get_or_create(
#                            post=fp, 
#                            fbuser=fbuser)
#        if created:
#            like.save()
#        if fp.post_from:
#            inc_co_occurrence(fp, fp.post_from, fbuser)
#        
#def process_shares(user, fp, shares):
#    fp.share_count = shares.get('count', 0)
#    # need more here
#  
#def process_comments(user, fp, comments):
#    # NOTE: add paging
#    data = comments.get('data', [])
#    for item in data:
#        comment_id = item['id']
#        fbuser = get_fbuser(int(item['from']['id']), item['from']['name'])
#        comment, created = Comment.objects.get_or_create(
#                                post=fp, 
#                                comment_id=comment_id,
#                                fbuser=fbuser)
#        if created:
#            comment.created_time = parser.parse(item['created_time'])
#            comment.message = item['message']
#        comment.like_count = item['like_count']
#        comment.user_likes = item['user_likes']
#        comment.save()
#        if fp.post_from:
#            inc_co_occurrence(fp, fp.post_from, fbuser)


#def _make_friend_activity(user, friend, date):
#    activity, created = FriendFeedActivity.objects.get_or_create(
#                                user=user,
#                                friend=friend,
#                                date=date)
#    if created:
#        activity.save()
#        # not ideal!
#        friendset, fscreated = FriendSet.objects.get_or_create(user=user)
#        friendset.friends.add(friend)
#        friendset.save()
#    return activity

#def daily_friend_data(user, friend, start, end):
#    activity_period = FriendFeedActivity.objects.filter(user=user,
#                        friend=friend,
#                        date__gte=start, date__lte=end).order_by('date')
#    activity_data = []
#    model_data = {}
#    ord_date = start.toordinal()
#    prev = ord_date-1
#    for daily_activity in activity_period:
#        ord_date = daily_activity.date.toordinal()
#        gap = ord_date-prev
#        if gap > 1:
#            tmp_date = prev+1
#            activity_data.append({'x':ordinal_to_timestamp(tmp_date), 'y':0})
#        if gap > 2:
#            tmp_date = ord_date-1
#            activity_data.append({'x':ordinal_to_timestamp(tmp_date), 'y':0})
#        timestamp = ordinal_to_timestamp(ord_date)
#        activity_data.append(
#            {'x':timestamp,
#            'y':daily_activity.chars}) # not right
#        model_data[timestamp] = daily_activity.id
#        prev = ord_date
#    end_ord = end.toordinal()
#    gap = end_ord - ord_date
#    if gap > 0:
#        activity_data.append({'x':ordinal_to_timestamp(ord_date+1), 'y':0})
#    if gap > 1:
#        activity_data.append({'x':ordinal_to_timestamp(end_ord), 'y':0})
#    return (activity_data, model_data)
#    
#def daily_friend_data_json(user, start, end):
#    friendset = FriendSet.objects.get(user=user)
#    data_series = []
#    for friend in friendset.friends.all():
#        activity_data, model_data = daily_friend_data(user, friend, start, end)
#        data_series.append({
#            'name': friend.anon_name,
#            'color': '#%s' % friend.colour,
#            'data': activity_data,
#            'models': model_data})
#    return json.dumps(data_series)
# 
#def get_co_occurrence(post, fbuser_a, fbuser_b):
#    if fbuser_a.user_id == fbuser_b.user_id:
#        return None
#    a = min(fbuser_a, fbuser_b, key=lambda x:x.user_id)
#    b = max(fbuser_a, fbuser_b, key=lambda x:x.user_id)
#    cooc, created = CoOccurrence.objects.get_or_create(
#                                post=post, fbuser_a=a, fbuser_b=b)
#    if created:
#        cooc.save()
#    return cooc

#def inc_co_occurrence(post, fbuser_a, fbuser_b):
#    cooc = get_co_occurrence(post, fbuser_a, fbuser_b)
#    if cooc:
#        cooc.count += 1
#        cooc.save()
#        return cooc
#    return None

# 
