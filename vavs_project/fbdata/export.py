# fbdata.export

# PYTHON
import StringIO

# UNICODECSV
import unicodecsv

# FBDATA
from .fbids import get_fbuser_from_djuser
from .utils import (
    fb_post_type_str,
    property_list_str
)

def collated_spreadsheet(data, anon=True, dialect='excel'):
    exportfile = StringIO.StringIO()
    writer = unicodecsv.writer(exportfile, dialect=dialect, encoding='utf-8')
    if isinstance(data, list):
        for entry in data:
            write_collated_data(writer, entry, anon)
    elif isinstance(data, dict):
        write_collated_data(writer, data, anon)
    exportdata = exportfile.getvalue()
    exportfile.close()
    return exportdata
    
def write_collated_data(writer, data, anon):
    # users
    writer.writerow(user_row_headings())
    writer.writerow(user_row_data(data['user'], data['fbuser'], anon))
    writer.writerow([])
    # posts
    writer.writerow(post_row_headings())
    for index, post in enumerate(data['posts']):
        writer.writerow(post_row_data(post, index+1, anon))
    writer.writerow([])
    writer.writerow(comment_row_headings())
    for index, comment in enumerate(data['post_comments']):
        writer.writerow(comment_row_data(comment, index+1, anon))
    writer.writerow([])
    # status
    writer.writerow(status_row_headings())
    for index, status in enumerate(data['status']):
        writer.writerow(status_row_data(status, index+1, anon))
    writer.writerow([])
    writer.writerow(comment_row_headings())
    for index, comment in enumerate(data['status_comments']):
        writer.writerow(comment_row_data(comment, index+1, anon))
    writer.writerow([])
    # link
    writer.writerow(link_row_headings())
    for index, link in enumerate(data['links']):
        writer.writerow(link_row_data(link, index+1, anon))
    writer.writerow([])
    writer.writerow(comment_row_headings())
    for index, comment in enumerate(data['link_comments']):
        writer.writerow(comment_row_data(comment, index+1, anon))
    writer.writerow([])
    # album
    writer.writerow(album_row_headings())
    for index, album in enumerate(data['albums']):
        writer.writerow(album_row_data(album, index+1, anon))
    writer.writerow([])
    writer.writerow(comment_row_headings())
    for index, comment in enumerate(data['album_comments']):
        writer.writerow(comment_row_data(comment, index+1, anon))
    writer.writerow([])
    # photo
    writer.writerow(photo_row_headings())
    for index, photo in enumerate(data['photos']):
        writer.writerow(photo_row_data(photo, index+1, anon))
    writer.writerow([])
    writer.writerow(comment_row_headings())
    for index, comment in enumerate(data['photo_comments']):
        writer.writerow(comment_row_data(comment, index+1, anon))
    writer.writerow([])
    writer.writerow(photo_tag_row_headings())
    for index, tag in enumerate(data['photo_tags']):
        writer.writerow(photo_tag_row_data(tag, index+1, anon))
    writer.writerow([])
    # video
    writer.writerow(video_row_headings())
    for index, video in enumerate(data['videos']):
        writer.writerow(video_row_data(video, index+1, anon))
    writer.writerow([])
    writer.writerow(comment_row_headings())
    for index, comment in enumerate(data['video_comments']):
        writer.writerow(comment_row_data(comment, index+1, anon))
    writer.writerow([])
    writer.writerow(video_tag_row_headings())
    for index, tag in enumerate(data['video_tags']):
        writer.writerow(video_tag_row_data(tag, index+1, anon))
    writer.writerow([])

def user_row_headings():
    return ['USER NAME', 'FACEBOOK NAME', 'ANON NAME', 'EMAIL', 'FACEBOOK ID', 'ANONYMISATION']
    
def user_row_data(user, fbuser, anon):
    return [
                user.get_full_name(),
                fbuser.user_name,
                fbuser.anon_name,
                user.email, 
                fbuser.user_id,
                'on' if anon else 'off'
            ]

def post_row_headings():
    return ['POST', 'POST ID', 'POST TYPE', 'FROM', 'CREATED', 'UPDATED', 'LIKES', 'LIKERS', 'TAGGED', 'COMMENTS', 'SHARES']
        
def post_row_data(post, index='', anon=True):
    name_prop = 'user_name' if anon else 'anon_name'
    return [
            index,
            post.post_id,
            fb_post_type_str(post.post_type),
            post.post_from.reference_name(anon),
            post.created_time,
            post.updated_time,
            post.like_count,
            '"%s"' % property_list_str(post.likers.all(), name_prop),
            '"%s"' % property_list_str(post.tagged.all(), name_prop),
            post.comment_count,
            post.share_count
        ]
        
def photo_row_headings():
    return ['PHOTO', 'OBJECT ID', 'ALBUM ID', 'OWNER', 'CREATED', 'UPDATED', 'LIKES', 'LIKERS', 'TAGGED', 'COMMENTS']
    
def photo_row_data(photo, index='', anon=True):
    name_prop = 'user_name' if anon else 'anon_name'
    return [
            index,
            photo.object_id,
            photo.album_object_id,
            photo.owner.reference_name(anon),
            photo.created_time,
            photo.updated_time,
            photo.like_count,
            '"%s"' % property_list_str(photo.likers.all(), name_prop),
            '"%s"' % property_list_str(photo.tagged.all(), name_prop),
            photo.comment_count
        ]

def photo_tag_row_headings():
    return ['PHOTO TAG', 'SOURCE ID', 'SUBJECT', 'CREATED', 'TEXT']
    
def photo_tag_row_data(tag, index='', anon=True):
    #name_prop = 'user_name' if anon else 'anon_name'
    return [
            index,
            tag.source.object_id,
            '' if anon else tag.subject,
            tag.created_time,
            '' if anon else tag.text
        ]
            
def video_row_headings():
    return ['VIDEO', 'VIDEO ID', 'ALBUM ID', 'OWNER', 'CREATED', 'UPDATED', 'LIKES', 'LIKERS', 'TAGGED', 'COMMENTS']
    
def video_row_data(video, index='', anon=True):
    name_prop = 'user_name' if anon else 'anon_name'
    return [
            index,
            video.video_id,
            video.album_id,
            video.owner.reference_name(anon),
            video.created_time,
            video.updated_time,
            video.like_count,
            '"%s"' % property_list_str(video.likers.all(), name_prop),
            '"%s"' % property_list_str(video.tagged.all(), name_prop),
            video.comment_count
        ]

def video_tag_row_headings():
    return ['VIDEO TAG', 'SOURCE ID', 'SUBJECT', 'CREATED']
    
def video_tag_row_data(tag, index='', anon=True):
    #name_prop = 'user_name' if anon else 'anon_name'
    return [
            index,
            tag.source.video_id,
            '' if anon else tag.subject,
            tag.created_time
        ]
                
def link_row_headings():
    return ['LINK', 'LINK ID', 'OWNER', 'VIA', 'URL', 'CREATED', 'LIKES', 'LIKERS', 'TAGGED', 'COMMENTS']
    
def link_row_data(link, index='', anon=True):
    name_prop = 'user_name' if anon else 'anon_name'
    return [
            index,
            link.link_id,
            link.owner.reference_name(anon),
            link.via.reference_name(anon) if link.via else '',
            link.url,
            link.created_time,
            link.like_count,
            '"%s"' % property_list_str(link.likers.all(), name_prop),
            '"%s"' % property_list_str(link.tagged.all(), name_prop),
            link.comment_count
        ]
        
def status_row_headings():
    return ['STATUS', 'STATUS ID', 'OWNER', 'MESSAGE', 'CREATED', 'LIKES', 'LIKERS', 'TAGGED', 'COMMENTS']
    
def status_row_data(status, index='', anon=True):
    name_prop = 'user_name' if anon else 'anon_name'
    return [
            index,
            status.status_id,
            status.owner.reference_name(anon),
            status.message if anon else '',
            status.created_time,
            status.like_count,
            '"%s"' % property_list_str(status.likers.all(), name_prop),
            '"%s"' % property_list_str(status.tagged.all(), name_prop),
            status.comment_count
        ]
        
def album_row_headings():
    return ['ALBUM', 'OBJECT ID', 'OWNER', 'NAME', 'CREATED', 'UPDATED', 'LIKES', 'LIKERS', 'TAGGED', 'COMMENTS']
    
def album_row_data(album, index='', anon=True):
    name_prop = 'user_name' if anon else 'anon_name'
    return [
            index,
            album.status_id,
            album.owner.reference_name(anon),
            album.name,
            album.created_time,
            album.updated_time,
            album.like_count,
            '"%s"' % property_list_str(album.likers.all(), name_prop),
            '"%s"' % property_list_str(album.tagged.all(), name_prop),
            album.comment_count
        ]
        
def comment_row_headings():
    return ['COMMENT', 'SOURCE', 'COMMENT ID', 'AUTHOR', 'CREATED', 'LIKES', 'LIKERS', 'TAGGED', 'MESSAGE']
  
def comment_row_data(comment, index='', anon=True):
    name_prop = 'user_name' if anon else 'anon_name'
    return [
            index,
            unicode(comment.source),
            comment.comment_id,
            comment.fbuser.reference_name(anon) if comment.fbuser else '',
            comment.created_time,
            comment.like_count,
            '"%s"' % property_list_str(comment.likers.all(), name_prop),
            '"%s"' % property_list_str(comment.tagged.all(), name_prop),
            '' if anon else '"%s"' % comment.message,
        ]
