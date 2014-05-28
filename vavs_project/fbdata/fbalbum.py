# fbdata.fbalbum

# FBDATA
from .fbcomments import (
    batch_comments,
    process_comments
)
from .fbids import get_fbuser
from .models import (
    FBAlbum,
    AlbumComment
)
from .utils import (
    links_from_str,
    timestamp_to_datetime
)

def collate_album_entries(user, start_date, end_date):
    return FBAlbum.objects.filter(
                            user=user, 
                            created_time__gte=start_date,
                            created_time__lte=end_date)
                            
def collate_album_comments(user, start_date, end_date):
    return AlbumComment.objects.filter(
                            source__user=user, 
                            created_time__gte=start_date,
                            created_time__lte=end_date)

def update_albums_for_user(user, graph, fbuser, start_time, end_time):
    albums = get_albums(user, graph, fbuser, start_time, end_time)
    lalbums = get_liked_albums(user, graph, fbuser, start_time, end_time)
    albums.extend(lalbums)
    batch_likes_for_albums(user, graph, albums)
    comments = batch_comments_for_albums(user, graph, albums) 
    return (albums, comments)
    
def get_albums(user, graph, owner, start_time, end_time):
    query = graph.fql('SELECT object_id, created, modified, name, description, link, like_info, comment_info FROM album WHERE owner=%s AND (created >= %d OR modified >= %d) AND created < %d' % (owner.user_id, start_time, start_time, end_time))
    return process_albums(user, query, owner=owner)

def get_liked_albums(user, graph, fbuser, start_time, end_time):
    query = graph.fql("SELECT object_id, owner, created, modified, name, description, link, like_info, comment_info FROM album WHERE object_id IN (SELECT object_id FROM like WHERE user_id = %s AND object_type = 'album') AND (created >= %d OR modified >= %d) AND created < %d" % (fbuser.user_id, start_time, start_time, end_time))
    return process_albums(user, query)
        
def get_album(user, graph, object_id):
    query = graph.fql('SELECT owner, created, modified, name, description, link, like_info, comment_info FROM album WHERE object_id=%s' % object_id)
    if query:
        data = query[0]
        owner = get_fbuser(data['owner'])
        return process_album(user, object_id, data, owner=owner)
    else:
        return None
           
def process_albums(user, query, owner=None):
    albums = []
    for data in query:
        object_id = data['object_id']
        album = process_album(user, object_id, data, owner=owner)
        albums.append(album)
    return albums
    
def process_album(user, object_id, data, owner=None):
    if not owner:
        owner = get_fbuser(data['owner'])
    created_time = timestamp_to_datetime(data['created'])
    updated_time = timestamp_to_datetime(data['modified'])
    album, created = FBAlbum.objects.get_or_create(
                                        user=user, 
                                        owner=owner,
                                        object_id=object_id,
                                        created_time=created_time)
    if created or album.needs_updated(updated_time):
        _update_album(album, updated_time, data)
        album.save()
    return album
    
def _update_album(album, updated_time, data):
    description = data.get('description', None)
    if description:
        album.description = description
    link = data.get('link', None)
    if link:
        album.link = link
    like_info = data.get('like_info', None)
    if like_info:
        album.like_count = data['like_info'].get('like_count', 0)
        album.user_likes = data['like_info'].get('user_likes', False)
    comment_info = data.get('comment_info', None)
    if comment_info:
        album.comment_count = data['comment_info'].get('comment_count', 0)
            
def get_comments_for_album(user, graph, album):
    comments_data = graph.fql("SELECT id, time, fromid, text, text_tags, likes, user_likes FROM comment WHERE object_id = '%s'" % album.object_id)
    return process_comments(user, graph, album, comments_data, AlbumComment)
    
def batch_comments_for_albums(user, graph, albums):
    return batch_comments(user, graph, albums, AlbumComment)
    
def get_likes_for_album(user, graph, album):
    from .fblikes import get_likes_for_object
    get_likes_for_object(user, graph, album, album.object_id)

def batch_likes_for_albums(user, graph, albums):
    from .fblikes import batch_likes_for_objects
    batch_likes_for_objects(user, graph, albums)        
