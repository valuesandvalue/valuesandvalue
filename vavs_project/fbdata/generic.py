# fbdata.generic

# FBDATA
from .models import (
    FBAlbum,
    FBEvent,
    FBLink,
    FBPhoto,
    FBStatus,
    FBVideo,
    StreamPost
)

_FB_CLASSES = {
    'album': FBAlbum,
    'event': FBEvent,
    'link': FBLink,
    'photo': FBPhoto,
    'status': FBStatus,
    'video': FBVideo,
    'post': StreamPost
}
def class_for_type(object_type):
    return _FB_CLASSES.get(object_type, None)

def album_exists(user, object_id):
    return FBAlbum.objects.filter(user=user, object_id=object_id).exists()
    
def event_exists(user, object_id):
    return FBEvent.objects.filter(user=user, event_id=object_id).exists()
    
def link_exists(user, link_id):
    return FBLink.objects.filter(user=user, link_id=link_id).exists()

def post_exists(user, post_id):
    return StreamPost.objects.filter(user=user, post_id=post_id).exists()
    
def photo_exists(user, object_id):
    return FBPhoto.objects.filter(user=user, object_id=object_id).exists()

def status_exists(user, status_id):
    return FBStatus.objects.filter(user=user, status_id=status_id).exists()
       
def video_exists(user, video_id):
    return FBVideo.objects.filter(user=user, video_id=video_id).exists()
   
