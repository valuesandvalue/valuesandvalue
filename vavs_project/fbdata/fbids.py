# fbdata.fbids

# DJANGO FACEBOOK
from django_facebook.models import FacebookUser, FacebookLike

# FBDATA
from .models import FBId
from .utils import (
    dict_of_objects,
    list_of_properties,
    quoted_list_str
)

UNCONNECTED = -1

def get_fbuser_name(user, graph, user_id, fbuser=None):
    if not fbuser:
        fbuser, created = FBId.objects.get_or_create(user_id=user_id)
    fbuser.users.add(user)
    fbuser.save()
    return fbuser
    
def get_facebook_graph(user):
    profile = user.get_profile()
    return profile.get_offline_graph()
    
def get_related_fbuser(user, other_id, other_name):
    try:
       return FacebookUser.objects.get(user_id=user.id, facebook_id=other_id)
    except FacebookUser.DoesNotExist:
        return FacebookUser.objects.create(
                user_id=UNCONNECTED, 
                facebook_id=other_id,
                name=other_name)
 
def get_fbuser(user_id, user_name=None, fb_type=None):
    fbuser, do_save = FBId.objects.get_or_create(user_id=user_id)
    if user_name and fbuser.user_name != user_name:
        fbuser.user_name = user_name
        do_save = True
    if fb_type and fbuser.fb_type != fb_type:
        fbuser.fb_type = fb_type
        do_save = True
    if do_save:
        fbuser.save()
    return fbuser

def get_fbuser_from_djuser(user):
    profile = user.get_profile()
    return get_fbuser(profile.facebook_id, profile.facebook_name)
    
def _connection_to_fbuser(user, connection):
    fb_id = connection['target_id']
    try:
        friend = FacebookUser.objects.get(user_id=user.id, facebook_id=fb_id)
    except FacebookUser.DoesNotExist:
        friend = None
    if not friend:
        try:
            friend = FacebookLike.objects.get(user_id=user.id, facebook_id=fb_id)
        except FacebookLike.DoesNotExist:
            friend = None
    fbuser, do_save = FBId.objects.get_or_create(user_id=fb_id)
    if friend:
        if not fbuser.user_name:
            fbuser.user_name = friend.name
            do_save = True
    if not fbuser.fb_type:
        fbuser.fb_type = connection['target_type']
        do_save = True
    if not fbuser.has_user(user):
        fbuser.users.add(user)
        do_save = True
    if do_save:
        fbuser.save()
    return fbuser
        
def get_connections(user, graph):
    connections = graph.fql('SELECT target_id, target_type FROM connection WHERE source_id = me()')
    fbusers = []
    for connection in connections:
        fbusers.append(_connection_to_fbuser(user, connection))
    return fbusers
    
def get_unnamed_fbids(user=None):
    if user:
        return FBId.objects.filter(
                    users=user, user_name__isnull=True, name_error=False)
    else:
        return FBId.objects.filter(user_name__isnull=True, name_error=False)
 
def batch_fbids(idlist, create_unknown=True):
    if not idlist:
        return FBId.objects.none()
    fbusers = FBId.objects.filter(user_id__in=idlist)
    if create_unknown:
        if isinstance(idlist[0], basestring):
            known = [unicode(u.user_id) for u in fbusers]
        else:
            known = [u.user_id for u in fbusers]
        unknown = list(set(idlist) - set(known))
        FBId.objects.bulk_create([FBId(user_id=fid) for fid in unknown])
        return FBId.objects.filter(user_id__in=idlist)
    else:
        return fbusers
        
def batch_fbnames(user, graph, fbusers, do_remote=True):
    idlist = [fbuser.user_id for fbuser in fbusers]
    fbuser_dict = dict_of_objects(fbusers, 'user_id')
    local = FacebookUser.objects.filter(facebook_id__in=idlist)
    named = set()
    for fu in local:
        fbuser = fbuser_dict[unicode(fu.facebook_id)]
        fbuser.user_name = fu.name
        fbuser.save()
        named.add(fbuser)
    unnamed = (set(fbusers) - named)
    if unnamed and do_remote:
        idlist_str = quoted_list_str(list_of_properties(unnamed, 'user_id'))
        query = graph.fql(
                    'SELECT uid, name FROM user WHERE uid IN (%s)' % idlist_str)
        for data in query:
            fbuser = FBId.objects.get(user_id=data['uid'])
            fbuser.user_name=data['name']
            fbuser.save()
            named.add(fbuser)
    return list(named)
    
def batch_unnamed(graph, unnamed):
    idlist_str = quoted_list_str(list_of_properties(unnamed, 'user_id'))
    query = graph.fql(
                'SELECT uid, name FROM user WHERE uid IN (%s)' % idlist_str)
    named = set()
    for data in query:
        fbuser = FBId.objects.get(user_id=data['uid'])
        fbuser.user_name=data['name']
        fbuser.save()
        named.add(fbuser)
    errors = (set(unnamed) - named)
    for fbuser in errors:
        fbuser.name_error= True
        fbuser.save()
    return (named, errors)
    
def load_user_friends(user):
    profile = user.get_profile()
    friends = profile.friends()
    idnames = {f.facebook_id:f.name for f in friends}
    idlist = idnames.keys()
    existing = FBId.objects.filter(user_id__in=idlist).values_list(
                                    'user_id', flat=True).order_by('user_id')
    missing = list(set(idlist) - set(existing))
    if missing:
        FBId.objects.bulk_create(
            [FBId(user_id=fid, user_name=idnames[fid]) for fid in missing])
            
def friend_ids(user):
    profile = user.get_profile()
    friends = profile.friends()
    return [f.facebook_id for f in friends]
