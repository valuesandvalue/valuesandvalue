# fbdata.fblinks

# FBDATA
from .fbcomments import (
    batch_comments,
    get_comments_for_object,
    process_comments
)
from .fbids import get_fbuser
from .fbtags import add_tagged_users
from .models import (
    FBId, 
    FBLink,
    LinkComment
)
from .utils import (
    dict_of_objects,
    links_from_str,
    list_of_properties,
    quoted_list_str,
    timestamp_to_datetime
)

def collate_link_entries(user, start_date, end_date):
    return FBLink.objects.filter(
                            user=user, 
                            created_time__gte=start_date,
                            created_time__lte=end_date)
                            
def collate_link_comments(user, start_date, end_date):
    return LinkComment.objects.filter(
                            source__user=user, 
                            created_time__gte=start_date,
                            created_time__lte=end_date)

def update_links_for_user(user, graph, fbuser, start_time, end_time):
    links = get_links(user, graph, fbuser, start_time, end_time)
    llinks = get_liked_links(user, graph, fbuser, start_time, end_time)
    links.extend(llinks)
    batch_stats_for_links(user, graph, links)
    batch_likes_for_links(user, graph, links)
    comments = batch_comments_for_links(user, graph, links)
    return (links, comments)
    
def get_links(user, graph, owner, start_time, end_time):
    query = graph.fql('SELECT link_id, via_id, created_time, url, owner_comment, summary, title, caption, like_info, comment_info FROM link WHERE owner=%s AND created_time >= %d AND created_time < %d' % (owner.user_id, start_time, end_time))
    return process_links(user, query, owner=owner)
    
def get_liked_links(user, graph, fbuser, start_time, end_time):
    query = graph.fql("SELECT link_id, owner, via_id, created_time, url, owner_comment, summary, title, caption, like_info, comment_info FROM link WHERE link_id IN (SELECT object_id FROM like WHERE user_id = %s AND object_type = 'link') AND created_time >= %d AND created_time < %d" % (fbuser.user_id, start_time, end_time))
    return process_links(user, query)
    
def process_links(user, query, owner=None):
    links = []
    for data in query:
        link_id = data['link_id']
        link = process_link(user, link_id, data, owner=owner)
        links.append(link)
    return links

def process_link(user, link_id, data, owner=None):
    if not owner:
        owner = get_fbuser(data['owner'])
    created_time = timestamp_to_datetime(data['created_time'])
    link, created = FBLink.objects.get_or_create(
                                        user=user, 
                                        owner=owner,
                                        link_id=link_id,
                                        created_time=created_time)
    do_save = _update_link(link, data)
    if created or do_save:
        link.save()
    return link
    
def get_link(user, graph, link_id):
    query = graph.fql('SELECT owner, via_id, created_time, url, owner_comment, summary, title, caption, like_info, comment_info FROM link WHERE link_id=%s' % link_id)
    if query:
        data = query[0]
        owner = get_fbuser(data['owner'])
        return process_link(user, link_id, data, owner=owner)
    else:
        return None
    
def _update_link(link, data):
    do_save = False
    url = data.get('url', None)
    if url and url != link.url:
        link.url = url
        do_save = True
    caption = data.get('caption', None)
    if caption and caption != link.caption:
        link.caption = caption
        do_save = True
    owner_comment = data.get('owner_comment', None)
    if owner_comment and owner_comment != link.owner_comment:
        link.owner_comment = owner_comment
        do_save = True
    summary = data.get('summary', None)
    if summary and summary != link.summary:
        link.summary = summary
        do_save = True
    title = data.get('title', None)
    if title and title != link.title:
        link.title = title
        do_save = True
    like_info = data.get('like_info', None)
    if like_info:
        like_count = data['like_info'].get('like_count', 0)
        user_likes = data['like_info'].get('user_likes', False)
        if like_count != link.like_count:
            link.like_count = like_count
            do_save = True
        if user_likes != link.user_likes:
            link.user_likes = user_likes
            do_save = True
    comment_info = data.get('comment_info', None)
    if comment_info:
        comment_count = data['comment_info'].get('comment_count', 0)
        if comment_count != link.comment_count:
            link.comment_count = comment_count
            do_save = True
    return do_save
   
def get_comments_for_link(user, graph, link):
    comments_data = get_comments_for_object(graph, link.link_id)
    return process_comments(user, graph, link, comments_data, LinkComment)
    
def batch_comments_for_links(user, graph, links):
    return batch_comments(user, graph, links, LinkComment, obj_id='link_id')
    
def get_likes_for_link(user, graph, link):
    from .fblikes import get_likes_for_object
    get_likes_for_object(user, graph, link, link.link_id)

def batch_likes_for_links(user, graph, links):
    from .fblikes import batch_likes_for_objects
    batch_likes_for_objects(user, graph, links, obj_id='link_id')      
        
def batch_stats_for_links(user, graph, links):
    link_urls_str = quoted_list_str(list_of_properties(links, 'url'))
    link_dict = dict_of_objects(links, 'url')
    query = graph.fql("SELECT url, click_count, share_count FROM link_stat WHERE url IN (%s)" % link_urls_str)
    for data in query:
        link = link_dict[unicode(data['url'])]
        link.click_count = data.get('click_count', 0)
        link.share_count = data.get('share_count', 0)
        link.save()
