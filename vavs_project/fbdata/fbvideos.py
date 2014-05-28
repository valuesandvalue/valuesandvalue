# fbdata.fbvideos

# FBDATA
from .fbcomments import (
    batch_comments,
    process_comments
)
from .fbids import get_fbuser
from .fbtags import add_tagged_id
from .models import (
    FBId, 
    FBVideo,
    VideoComment,
    VideoTag
)
from .utils import (
    dict_of_objects,
    links_from_str,
    list_of_properties,
    quoted_list_str,
    timestamp_to_datetime
)

def collate_video_entries(user, start_date, end_date):
    return FBVideo.objects.filter(
                            user=user, 
                            created_time__gte=start_date,
                            created_time__lte=end_date)
                            
def collate_video_comments(user, start_date, end_date):
    return VideoComment.objects.filter(
                            source__user=user, 
                            created_time__gte=start_date,
                            created_time__lte=end_date)
                            
def collate_video_tags(user, start_date, end_date):
    return VideoTag.objects.filter(
                            source__user=user, 
                            created_time__gte=start_date,
                            created_time__lte=end_date)
                            
def update_videos_for_user(user, graph, fbuser, start_time, end_time):
    videos = get_videos(user, graph, fbuser, start_time, end_time)
    lvideos = get_liked_videos(user, graph, fbuser, start_time, end_time)
    videos.extend(lvideos)
    batch_likes_for_videos(user, graph, videos)
    comments = batch_comments_for_videos(user, graph, videos)
    tags = batch_tags_for_videos(user, graph, videos)
    return (videos, comments, tags)
    
def get_videos(user, graph, owner, start_time, end_time):
    query = graph.fql('SELECT vid, album_id, created_time, updated_time, link, src, title, description FROM video WHERE owner=%s AND (created_time >= %d OR updated_time >= %d) AND created_time < %d' % (owner.user_id, start_time, start_time, end_time))
    return process_videos(user, query, owner=owner)
    
def get_liked_videos(user, graph, fbuser, start_time, end_time):
    query = graph.fql("SELECT vid, owner, album_id, created_time, updated_time, link, src, title, description FROM video WHERE vid IN (SELECT object_id FROM like WHERE user_id = %s AND object_type = 'video') AND (created_time >= %d OR updated_time >= %d) AND created_time < %d" % (fbuser.user_id, start_time, start_time, end_time))
    return process_videos(user, query)

def get_video(user, graph, video_id):
    query = graph.fql('SELECT owner, album_id, created_time, updated_time, link, src, title, description FROM video WHERE vid=%s' % video_id)
    if query:
        data = query[0]
        owner = get_fbuser(data['owner'])
        return process_video(user, video_id, data, owner=owner)
    else:
        return None
            
def process_videos(user, query, owner=None):
    videos = []
    for data in query:
        video_id = data['vid']
        video = process_video(user, video_id, data, owner=owner)
        videos.append(video)
    return videos

def process_video(user, video_id, data, owner=None):
    if not owner:
        owner = get_fbuser(data['owner'])
    album_id = data['album_id'] or ''
    created_time = timestamp_to_datetime(data['created_time'])
    updated_time = timestamp_to_datetime(data['updated_time'])
    video, created = FBVideo.objects.get_or_create(
                                        user=user, 
                                        owner=owner,
                                        video_id=video_id,
                                        album_id=album_id,
                                        created_time=created_time)
    if created or video.needs_updated(updated_time):
        _update_video(video, updated_time, data)
        video.save()
    return video
    
def _update_video(video, updated_time, data):
    video.updated_time = updated_time
    link = data.get('link', None)
    if link:
        video.link = link
    title = data.get('title', None)
    if title:
        video.title = title
    description = data.get('description', None)
    if description:
        video.description = description
    description = data.get('description', None)
    if description:
        video.description = description

def get_tags_for_video(user, graph, video):
    query = graph.fql('SELECT subject FROM video_tag WHERE vid=%s' % video.video_id)
    for data in query:
        user_id = data.get('subject', None)
        if user_id:
            print 'user_id', user_id
            add_tagged_id(post, user_id)

def get_comments_for_video(user, graph, video):
    comments_data = graph.fql("SELECT id, time, fromid, text, text_tags, likes, user_likes FROM comment WHERE object_id = '%s'" % video.video_id)
    return process_comments(user, graph, video, comments_data, VideoComment)
    
def batch_comments_for_videos(user, graph, videos):
    return batch_comments(user, graph, videos, VideoComment, obj_id='video_id')
             
def get_likes_for_video(user, graph, video):
    from .fblikes import get_likes_for_object
    get_likes_for_object(user, graph, video, video.video_id)

def batch_likes_for_videos(user, graph, videos):
    from .fblikes import batch_likes_for_objects
    batch_likes_for_objects(user, graph, videos, obj_id='video_id')
    
def batch_tags_for_videos(user, graph, videos):
    video_ids_str = quoted_list_str(list_of_properties(videos, 'video_id'))
    video_dict = dict_of_objects(videos, 'video_id')
    query = graph.fql('SELECT vid, subject, created_time FROM video_tag WHERE vid IN (%s)' % video_ids_str)
    tags = []
    for data in query:
        video = video_dict[unicode(data['vid'])]
        created = data.get('created_time', None)
        if created:
            created_time = timestamp_to_datetime(created)
        else:
            created_time = video.created_time
        subject = data['subject']
        tag, created = VideoTag.objects.get_or_create(source=photo, 
                                                subject=subject,
                                                created_time=created_time)
        if created:
            tag.save()
        tags.append(tag)
    return tags
