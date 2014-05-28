# fbdata.collation

# DJANGO-FACEBOOK
from open_facebook.exceptions import (
    OAuthException,
    OpenFacebookException
)

# FBDATA
from .fbalbum import (
    collate_album_comments,
    collate_album_entries,
    update_albums_for_user
)
from .fblinks import (
    collate_link_comments,
    collate_link_entries,
    update_links_for_user
)
from .fbevents import (
    collate_event_entries,
    update_events_for_user
)
from .fbphotos import (
    collate_photo_comments,
    collate_photo_entries,
    collate_photo_tags,
    update_photos_for_user
)
from .fbposts import (
    collate_post_comments,
    collate_post_entries,
    update_posts_for_user
)
from .fbstatus import (
    collate_status_comments,
    collate_status_entries,
    update_status_for_user
)
from .fbvideos import (
    collate_video_comments,
    collate_video_entries,
    collate_video_tags,
    update_videos_for_user
)
from .fbids import get_fbuser_from_djuser
from .utils import date_to_timestamp

def collate_updates(user, start_date, end_date=None, collate=False):
    end_date = end_date or start_date
    profile = user.get_profile()
    if profile.new_token_required:
        # request new token?
        print 'new_token_required'
        return False
    graph = profile.get_offline_graph()
    auth = False
    try:
        auth = graph.is_authenticated()
    except OAuthException, e:
        print e
    except OpenFacebookException, e:
        print e
    if not auth:
        return False
    fbuser = get_fbuser_from_djuser(user)
    start_time = int(date_to_timestamp(start_date))
    end_time = int(date_to_timestamp(end_date))
    posts, post_comments =  update_posts_for_user(
                    user, graph, fbuser, start_time, end_time)
    status, status_comments = update_status_for_user(
                    user, graph, fbuser, start_time, end_time)
    albums, album_comments = update_albums_for_user(
                    user, graph, fbuser, start_time, end_time)
    photos, photo_comments, photo_tags = update_photos_for_user(
                    user, graph, fbuser, start_time, end_time)
    videos, video_comments, video_tags = update_videos_for_user(
                    user, graph, fbuser, start_time, end_time)
    links, link_comments = update_links_for_user(
                    user, graph, fbuser, start_time, end_time)
    events = update_events_for_user(user, graph, fbuser, start_time, end_time)
    if collate:
        return {
            'user': user,
            'fbuser': fbuser,
            'start_date': start_date,
            'end_date': end_date,
            'posts': posts,
            'post_comments': post_comments,
            'status': status,
            'status_comments': status_comments,
            'albums': albums,
            'album_comments': album_comments,
            'photos': photos,
            'photo_comments': photo_comments,
            'photo_tags': photo_tags,
            'videos': videos,
            'video_comments': video_comments,
            'video_tags': video_tags,
            'links': links,
            'link_comments': link_comments,
            'events': events
        }
    else:
        return True
        
def collate_entries(user, start_date, end_date=None):
    end_date = end_date or start_date
    fbuser = get_fbuser_from_djuser(user)
    posts = collate_post_entries(user, start_date, end_date)
    post_comments = collate_post_comments(user, start_date, end_date)
    status = collate_status_entries(user, start_date, end_date)
    status_comments = collate_status_comments(user, start_date, end_date)
    albums = collate_album_entries(user, start_date, end_date)
    album_comments = collate_album_comments(user, start_date, end_date)
    photos = collate_photo_entries(user, start_date, end_date)
    photo_comments = collate_photo_comments(user, start_date, end_date)
    photo_tags = collate_photo_tags(user, start_date, end_date)
    videos = collate_video_entries(user, start_date, end_date)
    video_comments = collate_video_comments(user, start_date, end_date)
    video_tags = collate_video_tags(user, start_date, end_date)
    links = collate_link_entries(user, start_date, end_date)
    link_comments = collate_link_comments(user, start_date, end_date)
    events = collate_event_entries(user, start_date, end_date)
    return {
        'user': user,
        'fbuser': fbuser,
        'start_date': start_date,
        'end_date': end_date,
        'posts': posts,
        'post_comments': post_comments,
        'status': status,
        'status_comments': status_comments,
        'albums': albums,
        'album_comments': album_comments,
        'photos': photos,
        'photo_comments': photo_comments,
        'photo_tags': photo_tags,
        'videos': videos,
        'video_comments': video_comments,
        'video_tags': video_tags,
        'links': links,
        'link_comments': link_comments,
        'events': events
    }
    
