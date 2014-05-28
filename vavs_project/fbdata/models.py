# fbdata.models

# PYTHON
from datetime import timedelta

# DJANGO
from django.conf import settings
from django.core.paginator import Paginator
from django.db import models

# DJANGO FACEBOOK
from django_facebook.models import FacebookProfile

# FBDATA
from .fields import IntegerListField
from .utils import (
    date_to_timestamp,
    empty_hours, 
    fb_post_type_str, 
    get_choice_name,
    padded_date_range,
    random_color,
    truncate_html,
    wordlist_regex,
    LONG_DATE_FORMAT
)

############
# CLASSES
############    
class AnonName(models.Model):
    name = models.CharField(max_length=16, unique=True)
    
    def __unicode__(self):
        return self.name
        
def _anon_name():
    return '%s %s' % tuple(AnonName.objects.all().order_by('?')[:2])
    
class FBId(models.Model):
    user_id = models.BigIntegerField(unique=True)
    user_name = models.CharField(max_length=128, null=True, blank=True)
    anon_name = models.CharField(max_length=34, default=_anon_name)
    fb_type = models.CharField(max_length=12, null=True, blank=True)
    colour = models.CharField(max_length=6, default=random_color)
    users = models.ManyToManyField(settings.AUTH_USER_MODEL, 
                        related_name='friend_set')
    name_error = models.BooleanField(default=False)
                        
    def is_participant(self):
        return FacebookProfile.objects.filter(facebook_id=self.user_id).exists()
                        
    def reference_name(self, anon=True):
        return self.anon_name if anon else self.user_name or unicode(self.user_id)
        
    def reference_id(self, anon=True):
        return self.pk
                        
    def has_user(self, user):
        return self.users.filter(pk=user.pk).exists()
    
    def __unicode__(self):
        return '%s %s' % (self.user_name or 'Unknown', self.user_id)
        
    def detail_data(self, anon=True):
        return {'fbid': self.user_id,
                'name': self.user_name,
                'anon': self.anon_name,
                'type': self.fb_type,
                'rgb': self.colour,
                'users': [ u.id for u in self.users.all()],
                'participant': self.is_participant()}
        

class UserAnalysis(models.Model):
    STATUS_ERROR = 0
    STATUS_NEW = 1
    STATUS_SUCCESS = 2
    STATUS_UNDERTIME = -1
    STATUS_CHOICES = (
        (STATUS_ERROR, 'error'),
        (STATUS_NEW, 'new'),
        (STATUS_SUCCESS, 'success'),
        (STATUS_UNDERTIME, 'under time')
    )
    user = models.OneToOneField(settings.AUTH_USER_MODEL)
    fbuser = models.ForeignKey('FBId', null=True)
    anon_data = models.BooleanField(default=True)
    start_time = models.DateTimeField(null=True)
    end_time = models.DateTimeField(null=True)
    status = models.SmallIntegerField(choices=STATUS_CHOICES,
                                    default=STATUS_NEW)
    consent = models.BooleanField(default=False)
    page_size = 14.0
    
    def status_str(self):
        return get_choice_name(self.status, self.STATUS_CHOICES)
    
    def page_dates(self, page):
        if self.start_time:
            page = max(0, min(page, self.get_pages())-1)
            days = int(page * self.page_size)
            page_start = min(self.end_time, self.start_time + timedelta(days=days))
            page_end = page_start + timedelta(days=self.page_size)
            return padded_date_range(page_start, page_end)
        return (None, None)
    
    def get_pages(self):
        from math import ceil
        if not self.start_time or not self.end_time:
            return 0
        duration = self.end_time - self.start_time
        return int(ceil(duration.days / self.page_size))
        
    def end_page(self):
        return self.get_pages()
    
    def ad_topics(self):
        return AdTopic.objects.filter(users=self.user).order_by('label')
    
    def ad_topic_labels(self):
        return AdTopic.objects.filter(
                    users=self.user).values_list(
                    'label', flat=True).order_by('label')
        
    def match_ad_topics(self, input_str):
        if not self.ad_regex:
            self.ad_regex = wordlist_regex(self.ad_topic_labels())
        topics = self.ad_regex.findall(input_str)
        return topics
        
    def paginate(self, page=None):
        self.paginator = Paginator(range(1, self.get_pages()+1), 1)
        page = page or self.end_page()
        return self.paginator.page(page)
        
    def recent_time_frame(self):
        return self.page_dates(self.end_page())
    
class AdTopic(models.Model):
    users = models.ManyToManyField(settings.AUTH_USER_MODEL)
    label = models.CharField(max_length=128)
    
class StreamPost(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    post_id = models.CharField(max_length=128)
    post_from = models.ForeignKey('FBId', null=True)
    permalink = models.CharField(max_length=256, null=True, blank=True)
    post_type = models.PositiveIntegerField(default=0)
    created_time = models.DateTimeField(null=True)
    updated_time = models.DateTimeField(null=True)
    user_likes = models.BooleanField(default=False)
    like_count = models.PositiveIntegerField(default=0)
    comment_count = models.PositiveIntegerField(default=0)
    share_count = models.PositiveIntegerField(default=0)
    message = models.TextField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    likers = models.ManyToManyField('FBId', related_name='liked_posts')
    tagged = models.ManyToManyField('FBId', related_name='tagged_posts')
    
    @classmethod
    def comment_class(cls):
        return PostComment
        
    def get_comments(self):
        return self.postcomment_set.filter(
                   created_time__gte=self.created_time).order_by('created_time')
        
    @classmethod
    def type_str(cls):
        return 'post'
    
    def fbid(self):
        return self.post_id
        
    def fb_source_id(self, anon=True):
        return self.post_from.reference_id(anon)
        
    def fb_source(self):
        return self.post_from
        
    def fb_timestamp(self):
        return date_to_timestamp(self.created_time)
        
    def detail_data(self, anon=True):
        data = {'fbid': self.fbid(),
                'type': 'post',
                'post_type': self.post_type,
                'source_id': self.post_from.reference_id(anon),
                'source_name': self.post_from.reference_name(anon),
                'created_time': date_to_timestamp(self.created_time),
                'updated_time': date_to_timestamp(self.updated_time),
                'user_likes': self.user_likes,
                'like_count': self.like_count,
                'comment_count': self.comment_count,
                'share_count': self.share_count,
                'likers': [u.reference_id(anon) for u in self.likers.all()],
                'tagged': [u.reference_id(anon) for u in self.tagged.all()]}
        if not anon:
            data['permalink'] = self.permalink
            if self.message:
                data['message'] = truncate_html(self.message)
            if self.description:
                data['description'] = truncate_html(self.description)
        return data
    
    def needs_updated(self, updated_time):
        if self.updated_time:
            return self.updated_time < updated_time
        else:
            return True
            
    def get_reference_hour(self):
        rtime = self.updated_time or self.created_time
        return rtime.hour
        
    def time_str(self):
        return self.created_time.strftime(LONG_DATE_FORMAT)
        
    def post_type_str(self):
        return fb_post_type_str(self.post_type, default='status') 
        
    def __unicode__(self):
        return u'post: %s' % self.post_id
        
    def display_info(self, anon=True):
        title = None
        if not anon:
            if self.message:
                title = truncate_html(self.message)
            elif self.description:
                title = self.description
        if title:
            return u'%s %s: %s' % (self.time_str(), self.post_type_str(), title)
        else:
            return u'%s %s' % (self.time_str(), self.post_type_str())

class FBPhoto(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    object_id = models.CharField(max_length=128)
    album_object_id = models.CharField(max_length=128)
    owner = models.ForeignKey('FBId', null=True)
    link = models.CharField(max_length=256, null=True, blank=True)
    src = models.CharField(max_length=256, null=True, blank=True)
    created_time = models.DateTimeField(null=True)
    updated_time = models.DateTimeField(null=True)
    user_likes = models.BooleanField(default=False)
    like_count = models.PositiveIntegerField(default=0)
    comment_count = models.PositiveIntegerField(default=0)
    caption = models.TextField(null=True, blank=True)
    likers = models.ManyToManyField('FBId', related_name='liked_photos')
    tagged = models.ManyToManyField('FBId', related_name='tagged_photos')
    
    @classmethod
    def comment_class(cls):
        return PhotoComment
        
    def get_comments(self):
        return self.photocomment_set.filter(
                   created_time__gte=self.created_time).order_by('created_time')
        
    @classmethod
    def type_str(cls):
        return 'photo' 
        
    def fbid(self):
        return self.object_id
        
    def fb_source_id(self, anon=True):
        return self.owner.reference_id(anon)
        
    def fb_source(self):
        return self.owner
        
    def fb_timestamp(self):
        return date_to_timestamp(self.created_time)
    
    def __unicode__(self):
        return u'photo: %s' % self.object_id
    
    def detail_data(self, anon=True):
        data = {'fbid': self.object_id,
                'type': 'photo',
                'source_id': self.owner.reference_id(anon),
                'source_name': self.owner.reference_name(anon),
                'created_time': date_to_timestamp(self.created_time),
                'updated_time': date_to_timestamp(self.updated_time),
                'user_likes': self.user_likes,
                'like_count': self.like_count,
                'comment_count': self.comment_count,
                'likers': [ u.reference_id(anon) for u in self.likers.all()],
                'tagged': [ u.reference_id(anon) for u in self.tagged.all()]}
        if not anon:
            data['link'] = self.link
            data['src'] = self.src
            if self.caption:
                data['caption'] = truncate_html(self.caption)
        return data
    
    def needs_updated(self, updated_time):
        if self.updated_time:
            return self.updated_time < updated_time
        else:
            return True
            
    def get_reference_hour(self):
        rtime = self.updated_time or self.created_time
        return rtime.hour
    
    def time_str(self):
        return self.created_time.strftime(LONG_DATE_FORMAT)

    def display_info(self, anon=True):
        title = None
        if not anon:
            if self.caption:
                title = truncate_html(self.caption)
        if title:
            return u'%s %s: %s' % (self.time_str(), self.type_str(), title)
        else:
            return u'%s %s' % (self.time_str(), self.type_str())

class FBVideo(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    video_id = models.CharField(max_length=128)
    album_id = models.CharField(max_length=128)
    owner = models.ForeignKey('FBId', null=True)
    link = models.CharField(max_length=256, null=True, blank=True)
    src = models.CharField(max_length=256, null=True, blank=True)
    created_time = models.DateTimeField(null=True)
    updated_time = models.DateTimeField(null=True)
    user_likes = models.BooleanField(default=False)
    like_count = models.PositiveIntegerField(default=0)
    comment_count = models.PositiveIntegerField(default=0)
    title = models.CharField(max_length=256, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    likers = models.ManyToManyField('FBId', related_name='liked_videos')
    tagged = models.ManyToManyField('FBId', related_name='tagged_videos')
    
    @classmethod
    def comment_class(cls):
        return VideoComment
        
    def get_comments(self):
        return self.videocomment_set.filter(
                   created_time__gte=self.created_time).order_by('created_time')
                   
    @classmethod
    def type_str(cls):
        return 'video'
        
    def fbid(self):
        return self.video_id
        
    def fb_source_id(self, anon=True):
        return self.owner.reference_id(anon)
        
    def fb_source(self):
        return self.owner
        
    def fb_timestamp(self):
        return date_to_timestamp(self.created_time)
        
    def __unicode__(self):
        return u'video: %s' % self.video_id
    
    def detail_data(self, anon=True):
        data = {'fbid': self.video_id,
                'type': 'video',
                'source_id': self.owner.reference_id(anon),
                'source_name': self.owner.reference_name(anon),
                'created_time': date_to_timestamp(self.created_time),
                'updated_time': date_to_timestamp(self.updated_time),
                'user_likes': self.user_likes,
                'like_count': self.like_count,
                'comment_count': self.comment_count,
                'likers': [ u.reference_id(anon) for u in self.likers.all()],
                'tagged': [ u.reference_id(anon) for u in self.tagged.all()]}
        if not anon:
            data['link'] = self.link
            data['src'] = self.src
            if self.title:
                data['title'] = truncate_html(self.title)
            if self.description:
                data['description'] = truncate_html(self.description)
        return data
    
    def needs_updated(self, updated_time):
        if self.updated_time:
            return self.updated_time < updated_time
        else:
            return True
            
    def get_reference_hour(self):
        rtime = self.updated_time or self.created_time
        return rtime.hour
        
    def time_str(self):
        return self.created_time.strftime(LONG_DATE_FORMAT)
        
    def display_info(self, anon=True):
        title = None
        if not anon:
            title = self.title
        if title:
            return u'%s %s: %s' % (self.time_str(), self.type_str(), title)
        else:
            return u'%s %s' % (self.time_str(), self.type_str())

class FBLink(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    link_id = models.CharField(max_length=128)
    owner = models.ForeignKey('FBId', null=True)
    via = models.ForeignKey('FBId', null=True, related_name='link_shared')
    url = models.CharField(max_length=256, null=True, blank=True)
    created_time = models.DateTimeField(null=True)
    user_likes = models.BooleanField(default=False)
    like_count = models.PositiveIntegerField(default=0)
    comment_count = models.PositiveIntegerField(default=0)
    share_count = models.PositiveIntegerField(default=0)
    click_count = models.PositiveIntegerField(default=0)
    caption = models.TextField(null=True, blank=True)
    summary = models.TextField(null=True, blank=True)
    title = models.TextField(null=True, blank=True)
    owner_comment = models.TextField(null=True, blank=True)
    likers = models.ManyToManyField('FBId', related_name='liked_links')
    tagged = models.ManyToManyField('FBId', related_name='tagged_links')
    
    @classmethod
    def comment_class(cls):
        return LinkComment
        
    def get_comments(self):
        return self.linkcomment_set.filter(
                   created_time__gte=self.created_time).order_by('created_time')
        
    @classmethod
    def type_str(cls):
        return 'link' 
        
    def fbid(self):
        return self.link_id
        
    def fb_source_id(self, anon=True):
        return self.owner.reference_id(anon)
        
    def fb_source(self):
        return self.owner
        
    def fb_timestamp(self):
        return date_to_timestamp(self.created_time)
    
    def __unicode__(self):
        return u'link: %s' % self.link_id
    
    def detail_data(self, anon=True):
        data = {'fbid': self.link_id,
                'type': 'link',
                'source_id': self.owner.reference_id(anon),
                'source_name': self.owner.reference_name(anon),                
                'created_time': date_to_timestamp(self.created_time),
                'user_likes': self.user_likes,
                'like_count': self.like_count,
                'comment_count': self.comment_count,
                'share_count': self.share_count,
                'click_count': self.click_count,
                'likers': [ u.reference_id(anon) for u in self.likers.all()],
                'tagged': [ u.reference_id(anon) for u in self.tagged.all()]}
        if self.via:
            data['via_id'] = self.via.reference_id(anon)
            data['via_name'] = self.via.reference_name(anon)
        if not anon:
            data['url'] = self.url
            if self.title:
                data['title'] = truncate_html(self.title)
            if self.caption:
                data['caption'] = truncate_html(self.caption)
            if self.summary:
                data['summary'] = truncate_html(self.summary)
            if self.owner_comment:
                data['owner_comment'] = truncate_html(self.owner_comment)
        return data
    
    def needs_updated(self, updated_time):
        return True
            
    def get_reference_hour(self):
        return self.created_time.hour
        
    def time_str(self):
        return self.created_time.strftime(LONG_DATE_FORMAT)
        
    def display_info(self, anon=True):
        title = None
        if not anon:
            title = self.title
        if title:
            return u'%s %s: %s' % (self.time_str(), self.type_str(), title)
        else:
            return u'%s %s' % (self.time_str(), self.type_str())
    
class FBStatus(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    status_id = models.CharField(max_length=128)
    owner = models.ForeignKey('FBId', null=True)
    message = models.TextField(null=True, blank=True)
    created_time = models.DateTimeField(null=True)
    user_likes = models.BooleanField(default=False)
    like_count = models.PositiveIntegerField(default=0)
    comment_count = models.PositiveIntegerField(default=0)
    likers = models.ManyToManyField('FBId', related_name='liked_status')
    tagged = models.ManyToManyField('FBId', related_name='tagged_status')
    
    @classmethod
    def comment_class(cls):
        return StatusComment
        
    def get_comments(self):
        return self.statuscomment_set.filter(
                   created_time__gte=self.created_time).order_by('created_time')
        
    @classmethod
    def type_str(cls):
        return 'status' 
        
    def fbid(self):
        return self.status_id
        
    def fb_source_id(self, anon=True):
        return self.owner.reference_id(anon)
        
    def fb_source(self):
        return self.owner
        
    def fb_timestamp(self):
        return date_to_timestamp(self.created_time)
    
    def __unicode__(self):
        return u'status: %s' % self.status_id
    
    def detail_data(self, anon=True):
        data = {'fbid': self.status_id,
                'type': 'status',
                'source_id': self.owner.reference_id(anon),
                'source_name': self.owner.reference_name(anon),
                'created_time': date_to_timestamp(self.created_time),
                'user_likes': self.user_likes,
                'like_count': self.like_count,
                'comment_count': self.comment_count,
                'message': 'anonymised' if anon else truncate_html(self.message),
                'likers': [ u.reference_id(anon) for u in self.likers.all()],
                'tagged': [ u.reference_id(anon) for u in self.tagged.all()]}
        if not anon:
            if self.message:
                data['message'] = truncate_html(self.message)
        return data
    
    def needs_updated(self, updated_time):
        return True
            
    def get_reference_hour(self):
        return self.created_time.hour
        
    def time_str(self):
        return self.created_time.strftime(LONG_DATE_FORMAT)

    def display_info(self, anon=True):
        title = None
        if not anon:
            title = truncate_html(self.message)
        if title:
            return u'%s %s: %s' % (self.time_str(), self.type_str(), title)
        else:
            return u'%s %s' % (self.time_str(), self.type_str())
                        
class FBAlbum(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    object_id = models.CharField(max_length=128)
    owner = models.ForeignKey('FBId', null=True)
    link = models.CharField(max_length=256, null=True, blank=True)
    created_time = models.DateTimeField(null=True)
    updated_time = models.DateTimeField(null=True)
    user_likes = models.BooleanField(default=False)
    like_count = models.PositiveIntegerField(default=0)
    comment_count = models.PositiveIntegerField(default=0)
    description = models.TextField(null=True, blank=True)
    name = models.TextField(null=True, blank=True)
    likers = models.ManyToManyField('FBId', related_name='liked_albums')
    tagged = models.ManyToManyField('FBId', related_name='tagged_albums')
    
    @classmethod
    def comment_class(cls):
        return AlbumComment
        
    def get_comments(self):
        return self.albumcomment_set.filter(
                   created_time__gte=self.created_time).order_by('created_time')
        
    @classmethod
    def type_str(cls):
        return 'album' 
        
    def fbid(self):
        return self.object_id
        
    def fb_source_id(self, anon=True):
        return self.owner.reference_id(anon)
        
    def fb_source(self):
        return self.owner
        
    def fb_timestamp(self):
        return date_to_timestamp(self.created_time)
        
    def __unicode__(self):
        return u'album: %s' % self.object_id
    
    def detail_data(self, anon=True):
        data = {'fbid': self.object_id,
                'type': 'album',
                'source_id': self.owner.reference_id(anon),
                'source_name': self.owner.reference_name(anon),
                'created_time': date_to_timestamp(self.created_time),
                'user_likes': self.user_likes,
                'like_count': self.like_count,
                'comment_count': self.comment_count,
                'likers': [u.reference_id(anon) for u in self.likers.all()],
                'tagged': [u.reference_id(anon) for u in self.tagged.all()]}
        if self.updated_time:
            data['updated_time'] = date_to_timestamp(self.updated_time)
        if not anon:
            if self.link:
                data['link'] = self.link
            if self.description:
                data['description'] = truncate_html(self.description)
            if self.name:
                data['name'] = truncate_html(self.name)
        return data
            
    def needs_updated(self, updated_time):
        if self.updated_time:
            return self.updated_time < updated_time
        else:
            return True
            
    def get_reference_hour(self):
        rtime = self.updated_time or self.created_time
        return rtime.hour
        
    def time_str(self):
        return self.created_time.strftime(LONG_DATE_FORMAT)
        
    def display_info(self, anon=True):
        title = None
        if not anon:
            title = self.name
        if title:
            return u'%s %s: %s' % (self.time_str(), self.type_str(), title)
        else:
            return u'%s %s' % (self.time_str(), self.type_str())
                        
class FBEvent(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    event_id = models.CharField(max_length=128)
    creator = models.ForeignKey('FBId', null=True)
    name = models.TextField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    start_time = models.DateTimeField(null=True)
    end_time = models.DateTimeField(null=True)
    updated_time = models.DateTimeField(null=True)
    all_members_count = models.PositiveIntegerField(default=0)
    attending_count = models.PositiveIntegerField(default=0)
    declined_count = models.PositiveIntegerField(default=0)
    unsure_count = models.PositiveIntegerField(default=0)
    invited = models.ManyToManyField('FBId', related_name='invited_events')
    
    @classmethod
    def comment_class(cls):
        return None
        
    def get_comments(self):
        return []
        
    @classmethod
    def type_str(cls):
        return 'event' 
        
    def fbid(self):
        return self.event_id
        
    def fb_source_id(self, anon=True):
        return self.creator.reference_id(anon)
        
    def fb_source(self):
        return self.creator
        
    def fb_timestamp(self):
        return date_to_timestamp(self.updated_time)
    
    def __unicode__(self):
        return u'photo: %s' % self.object_id
    
    def detail_data(self, anon=True):
        return {'fbid': self.event_id,
                'type': 'event',
                'source_id': self.creator.reference_id(anon),
                'source_name': self.creator.reference_name(anon),
                'name': 'anonymised' if anon else truncate_html(self.name),
                'start_time': date_to_timestamp(self.start_time),
                'end_time': date_to_timestamp(self.end_time),
                'updated_time': date_to_timestamp(self.updated_time),
                'all_members_count': self.all_members_count,
                'attending_count': self.attending_count,
                'declined_count': self.declined_count,
                'unsure_count': self.unsure_count,
                'invited': [ u.reference_id(anon) for u in self.invited.all()]}
    
    def needs_updated(self, updated_time):
        if self.updated_time:
            return self.updated_time < updated_time
        else:
            return True
            
    def get_reference_hour(self):
        return self.start.hour
        
    def time_str(self):
        return self.created_time.strftime(LONG_DATE_FORMAT)
        
    def display_info(self, anon=True):
        title = None
        if not anon:
            title = self.name
        if title:
            return u'%s %s: %s' % (self.time_str(), self.type_str(), title)
        else:
            return u'%s %s' % (self.time_str(), self.type_str())
                 
####################
# COMMENTS
####################                               
class Comment(models.Model):
    comment_id = models.CharField(max_length=128)
    created_time = models.DateTimeField(null=True)
    fbuser = models.ForeignKey('FBId', null=True)
    like_count = models.PositiveIntegerField(default=0)
    user_likes = models.BooleanField(default=False)
    likers = models.ManyToManyField('FBId', related_name='liked_comments')
    message = models.TextField(null=True, blank=True)
    tagged = models.ManyToManyField('FBId', related_name='tagged_comments')
    
    def get_reference_hour(self):
        return self.created_time.hour
        
    def detail_data(self, anon=True):
        data = {'fbid': self.comment_id,
                'type': 'comment',
                'created_time': date_to_timestamp(self.created_time),
                'fromid': self.fbuser.reference_id(anon),
                'like_count': self.like_count,
                'user_likes': self.user_likes}
        if not anon:
            if self.message:
                data['message'] = truncate_html(self.message)
        return data

class PostComment(Comment):
    source = models.ForeignKey('StreamPost', null=True)
    
class PhotoComment(Comment):
    source = models.ForeignKey('FBPhoto', null=True)
    
class VideoComment(Comment):
    source = models.ForeignKey('FBVideo', null=True)
    
class LinkComment(Comment):
    source = models.ForeignKey('FBLink', null=True)
    
class StatusComment(Comment):
    source = models.ForeignKey('FBStatus', null=True)
  
class AlbumComment(Comment):
    source = models.ForeignKey('FBAlbum', null=True)

####################
# TAGS
#################### 
class PhotoTag(models.Model):
    source = models.ForeignKey('FBPhoto')
    subject = models.CharField(max_length=128)
    created_time = models.DateTimeField(null=True)
    text = models.TextField(null=True, blank=True)

class VideoTag(models.Model):
    source = models.ForeignKey('FBVideo')
    subject = models.CharField(max_length=128)
    created_time = models.DateTimeField(null=True)  
      
####################
# ACTIVITY
####################     
class DailyStreamActivity(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    date = models.DateField()
    posts = models.ManyToManyField('StreamPost')
    likes = models.PositiveIntegerField(default=0)
    shares = models.PositiveIntegerField(default=0)
    comments = models.PositiveIntegerField(default=0)
    fbusers = models.ManyToManyField('FBId')
    chars = models.PositiveIntegerField(default=0)
    hourly = IntegerListField(max_length=120, default=empty_hours)
                    
