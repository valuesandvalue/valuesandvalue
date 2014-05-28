# fbdata.fbtags

# FBDATA
from .fbids import get_fbuser
from .models import FBId

def add_tagged_users(fbobject, taglist):
    for tag in taglist:
        user_id = tag['id']
        user_name = tag['name']
        fb_type = tag['type']
        fbuser = get_fbuser(user_id, user_name, fb_type=fb_type)
        fbobject.tagged.add(fbuser)
        
def add_tagged_ids(post, taglist):
    for user_id in taglist:
        fbuser, created = FBId.objects.get_or_create(user_id=user_id)
        if created:
            fbuser.save()
        post.tagged.add(fbuser)
        
def add_tagged_id(post, user_id):
    fbuser, created = FBId.objects.get_or_create(user_id=user_id)
    if created:
        fbuser.save()
    post.tagged.add(fbuser)
