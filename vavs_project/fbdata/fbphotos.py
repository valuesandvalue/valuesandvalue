# fbdata.fbphotos

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
    FBPhoto,
    PhotoComment,
    PhotoTag
)
from .utils import (
    dict_of_objects,
    links_from_str,
    list_of_properties,
    quoted_list_str,
    timestamp_to_datetime
)

def collate_photo_entries(user, start_date, end_date):
    return FBPhoto.objects.filter(
                            user=user, 
                            created_time__gte=start_date,
                            created_time__lte=end_date)

def collate_photo_comments(user, start_date, end_date):
    return PhotoComment.objects.filter(
                            source__user=user, 
                            created_time__gte=start_date,
                            created_time__lte=end_date)

def collate_photo_tags(user, start_date, end_date):
    return PhotoTag.objects.filter(
                            source__user=user, 
                            created_time__gte=start_date,
                            created_time__lte=end_date)
                            
def update_photos_for_user(user, graph, fbuser, start_time, end_time):
    photos = get_photos(user, graph, fbuser, start_time, end_time)
    lphotos = get_liked_photos(user, graph, fbuser, start_time, end_time)
    photos.extend(lphotos)
    batch_likes_for_photos(user, graph, photos)
    comments = batch_comments_for_photos(user, graph, photos)
    tags = batch_tags_for_photos(user, graph, photos)
    return (photos, comments, tags)
    
def get_photos(user, graph, owner, start_time, end_time):
    query = graph.fql('SELECT object_id, album_object_id, created, modified, link, src, caption, caption_tags, like_info, comment_info FROM photo WHERE owner=%s AND (created >= %d OR modified >= %d) AND created < %d' % (owner.user_id, start_time, start_time, end_time))
    return process_photos(user, query, owner=owner)
    
def get_liked_photos(user, graph, fbuser, start_time, end_time):
    query = graph.fql("SELECT object_id, owner, album_object_id, created, modified, link, src, caption, caption_tags, like_info, comment_info FROM photo WHERE object_id IN (SELECT object_id FROM like WHERE user_id = %s AND object_type = 'photo') AND (created >= %d OR modified >= %d) AND created < %d" % (fbuser.user_id, start_time, start_time, end_time))
    return process_photos(user, query)
    
def get_photo(user, graph, object_id):
    query = graph.fql('SELECT owner, album_object_id, created, modified, link, src, caption, caption_tags, like_info, comment_info FROM photo WHERE object_id=%s' % object_id)
    if query:
        data = query[0]
        owner = get_fbuser(data['owner'])
        return process_photo(user, object_id, data, owner=owner)
    else:
        return None
           
def process_photos(user, query, owner=None):
    photos = []
    for data in query:
        object_id = data['object_id']
        photo = process_photo(user, object_id, data, owner=owner)
        photos.append(photo)
    return photos
    
def process_photo(user, object_id, data, owner=None):
    if not owner:
        owner = get_fbuser(data['owner'])
    created_time = timestamp_to_datetime(data['created'])
    updated_time = timestamp_to_datetime(data['modified'])
    photo, created = FBPhoto.objects.get_or_create(
                                        user=user, 
                                        owner=owner,
                                        object_id=object_id,
                                        created_time=created_time)
    if created or photo.needs_updated(updated_time):
        _update_photo(photo, updated_time, data)
        photo.save()
    return photo
    
def _update_photo(photo, updated_time, data):
    photo.updated_time = updated_time
    album_object_id = data.get('album_object_id', None)
    if album_object_id:
        photo.album_object_id = album_object_id
    link = data.get('link', None)
    if link:
        photo.link = link
    caption = data.get('caption', None)
    if caption:
        photo.caption = caption
    like_info = data.get('like_info', None)
    if like_info:
        photo.like_count = data['like_info'].get('like_count', 0)
        photo.user_likes = data['like_info'].get('user_likes', False)
    comment_info = data.get('comment_info', None)
    if comment_info:
        photo.comment_count = data['comment_info'].get('comment_count', 0)
    caption_tags = data.get('caption_tags', None)
    if caption_tags:
        for taglist in caption_tags.values():
            add_tagged_users(photo, taglist)
            
def get_comments_for_photo(user, graph, photo):
    comments_data = graph.fql("SELECT id, time, fromid, text, text_tags, likes, user_likes FROM comment WHERE object_id = '%s'" % photo.object_id)
    return process_comments(user, graph, photo, comments_data, PhotoComment)
    
def batch_comments_for_photos(user, graph, photos):
    return batch_comments(user, graph, photos, PhotoComment)
    
def get_likes_for_photo(user, graph, photo):
    from .fblikes import get_likes_for_object
    get_likes_for_object(user, graph, photo, photo.object_id)
    
def batch_likes_for_photos(user, graph, photos):
    from .fblikes import batch_likes_for_objects
    batch_likes_for_objects(user, graph, photos)
            
def batch_tags_for_photos(user, graph, photos):
    photo_ids_str = quoted_list_str(list_of_properties(photos, 'object_id'))
    photo_dict = dict_of_objects(photos, 'object_id')
    query = graph.fql('SELECT object_id, created, subject, text FROM photo_tag WHERE object_id IN (%s)' % photo_ids_str)
    tags = []
    for data in query:
        photo = photo_dict[unicode(data['object_id'])]
        created = data.get('created', None)
        if created:
            created_time = timestamp_to_datetime(created)
        else:
            created_time = photo.created_time
        subject = data['subject']
        text = data['text']
        tag, created = PhotoTag.objects.get_or_create(source=photo, 
                                                subject=subject,
                                                created_time=created_time,
                                                text=text)
        if created:
            tag.save()
        tags.append(tag)
    return tags
