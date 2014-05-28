# fbdata.graphs

# PYTHON
import json

# ADDATA
from addata.activity import get_activity_for_period
from addata.handlers import (
        get_user_fbads,
        get_user_fbsponsored,
        get_user_data
)

# FBDATA
from .collation import collate_entries
from .fbids import get_fbuser_from_djuser
from .models import (
    FBAlbum,
    FBEvent,
    FBLink,
    FBPhoto,
    FBStatus,
    FBVideo,
    StreamPost,
    PostComment,
    PhotoComment,
    VideoComment,
    LinkComment,
    StatusComment,
    AlbumComment
)
from .participant import get_participant_profile
from .utils import date_to_timestamp

class NarrativeData():
    def __init__(self, user, start_time, end_time, fbuser=None, anon=True):
        self.user = user
        self.start_time = start_time
        self.end_time = end_time
        self.fbuser = fbuser or get_fbuser_from_djuser(self.user)
        self.anon = anon
        self.users = {}
        self.friend_list = [fbuser]
        self._data_funcs = {
            'posts': self._collate_posts,
            'photos': self._collate_photos,
            'status': self._collate_status,
            'albums': self._collate_albums,
            'videos': self._collate_videos,
            'links': self._collate_links,
            'events': self._collate_events,
            'ads': self._collate_ads
        }
        
    def to_json(self):
        self.collate()
        return json.dumps({
            'source': self.fbuser.reference_name(self.anon),
            'source_pk': self.fbuser.pk,
            'dates': {'start': date_to_timestamp(self.start_time),
                    'end': date_to_timestamp(self.end_time)},
            'users': self.user_data,
            'fbobjects': self.fbobject_data,
            'fbads':self.fbads,
            'fbsps':self.fbsps,
            'ads':self.ads})
        
    def collate(self, data_types=None):
        self.fbobjects = []
        self.fbobject_data = []
        self.data = collate_entries(self.user, self.start_time, self.end_time)
        if not data_types:
            self._collate_all()
        else:
            for dt in data_types:
                func = self._data_funcs.get(dt, None)
                if func:
                    self.func()
            self._collate_users()
            
    def sort(self):
        pass
        
    def arrange(self):
        pass
        
    def cache(self):
        pass
        
    def get_cached(self):
        pass
        
    def _collate_ads(self):
        _ads = get_activity_for_period(
                                self.user, self.start_time, self.end_time)
        self.ads = [a.packed_data() for a in _ads]
        _fbads = get_user_fbads(self.user, self.start_time, self.end_time)
        self.fbads = [a.basic_data(anon=self.anon) for a in _fbads]
        _fbsps = get_user_fbsponsored(self.user, self.start_time, self.end_time)
        self.fbsps = [a.basic_data(anon=self.anon) for a in _fbsps]
        
    def _collate_all(self):
        self._collate_posts()
        self._collate_photos()
        self._collate_status()
        self._collate_albums()
        self._collate_videos()
        self._collate_links()
        self._collate_events()
        self._collate_users()
        self._collate_ads()

    def _collate_users(self):
        self.user_data = [
            {'name':f.reference_name(self.anon), 
            'id':f.id, 
            'rgb':'#%s'%f.colour,
            'nodes': self._sort_nodes(nodes)} for f, nodes in self.users.items()]

    def _sort_nodes(self, nodes):
        if nodes:
            nodes.sort(key=lambda a: a.fb_timestamp())
            return [n.id for n in nodes]
        else:
            return []
        
    def _add_user(self, fbuser, fbobject):
        if not self.users.has_key(fbuser):
            self.users[fbuser] = [fbobject]
        else:
            self.users[fbuser].append(fbobject)
        return fbuser.id
     
    def _collate_items(self, fbobject_list): 
        for fbobject in fbobject_list:
            friends = set(fbobject.likers.all())
            if fbobject.fb_source():
                friends.add(fbobject.fb_source())
            if fbobject.user_likes:
                friends.add(self.fbuser)
            for fbu in fbobject.tagged.all():
                friends.add(fbu)
            comment_class = fbobject.comment_class()
            comments_data = {}
            if comment_class:
                comments = comment_class.objects.filter(source=fbobject)
                for cm in comments:
                    friends.add(cm.fbuser)
                    user_id = cm.fbuser.user_id
                    comments_data[user_id] = comments_data.get(
                                                  user_id, 0) + len(cm.message)
            fbdata = {
                    'date': fbobject.fb_timestamp(),
                    'id': fbobject.id,
                    'type': fbobject.type_str(),
                    'from': fbobject.fb_source_id(self.anon),
                    'info': fbobject.display_info(self.anon),
                    }
            if friends:
                fbdata['users'] = [self._add_user(f, fbobject) for f in friends]
            if comments_data:
                fbdata['comments'] = comments_data
            if (hasattr(fbobject, 'like_count') and 
                    fbobject.like_count > len(fbdata['users'])):
                fbdata['plus'] = True
#            if (hasattr(fbobject, 'comment_count') and 
#                    fbobject.comment_count > len(fbdata['users'])):
#                fbdata['plus'] = True
            self.fbobject_data.append(fbdata)
            self.fbobjects.append(fbobject)
            
    def _collate_posts(self):
        self._collate_items(self.data['posts'])
        
    def _collate_photos(self):
        self._collate_items(self.data['photos'])
                           
    def _collate_videos(self):
        self._collate_items(self.data['videos'])
            
    def _collate_albums(self):
        self._collate_items(self.data['albums'])
        
    def _collate_links(self):
        self._collate_items(self.data['links'])
        
    def _collate_events(self):
        self._collate_items(self.data['events'])
        
    def _collate_status(self):
        self._collate_items(self.data['status'])

def narrative_data_json(user, start, end, fbuser=None, anon=True):
    fbuser = fbuser or get_fbuser_from_djuser(user)
    nd = NarrativeData(user, start, end, fbuser=fbuser, anon=anon)
    return nd.to_json()
