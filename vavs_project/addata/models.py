# addata.models

# PYTHON
from datetime import datetime
import json
import os

# DJANGO
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.utils.timezone import now

# FBDATA
from fbdata.utils import (
    date_to_timestamp,
    get_choice_name
)

class RawData(models.Model):
    DATA_NONE = 0
    DATA_URLS = 1
    DATA_COOKIES = 2
    DATA_FBADS = 3
    DATA_FB = 4
    DATA_FBLISTING = 5
    DATA_CHOICES = (
        (DATA_NONE, 'none'),
        (DATA_URLS, 'urls'),
        (DATA_COOKIES, 'cookies'),
        (DATA_FBADS, 'fbads'),
        (DATA_FB, 'fb'),
        (DATA_FBLISTING, 'fblisting')
    )
    STATUS_NEW = 0
    STATUS_DONE = 1
    STATUS_ERROR = 2
    STATUS_UNPROCESSED = 3
    STATUS_CHOICES = (
        (STATUS_NEW, 'new'),
        (STATUS_DONE, 'done'),
        (STATUS_ERROR, 'error'),
        (STATUS_UNPROCESSED, 'unprocessed'),
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True)
    created = models.DateTimeField(auto_now_add=True)
    datatype = models.SmallIntegerField(choices=DATA_CHOICES,
                                    default=DATA_NONE)
    data = models.TextField()
    status = models.SmallIntegerField(choices=STATUS_CHOICES,
                                    default=STATUS_NEW)
    error = models.TextField(null=True)
    
    def status_str(self):
        return get_choice_name(self.status, self.STATUS_CHOICES)

class DomainList(models.Model):
    name = models.CharField(max_length=24, unique=True)
    domains = models.ManyToManyField(
                        'DomainName', related_name='listed_domains')
    
    def __unicode__(self):
        return self.name
          
class DomainName(models.Model):
    name = models.CharField(max_length=128)
    
    def __unicode__(self):
        return self.name
        
    def ref_name(self, anon=True):
        return unicode(self.id) if anon else self.name
        
class FBSponsored(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    date = models.DateTimeField(default=now)
    actor = models.CharField(max_length=128, null=True)
    target = models.CharField(max_length=128, null=True)
    type_id = models.PositiveIntegerField(default=0)
    text = models.TextField(null=True)
    title = models.TextField()
    images = models.ManyToManyField('FBAdImage', related_name='sponsored_images')
    links = models.ManyToManyField('FBAdLink', related_name='sponsored_links')
    
    def basic_data(self, anon=True):
        return {'date': date_to_timestamp(self.date),
                'id': self.id,
                'title': self.title}
                
    def detail_data(self, anon=True):
        return {'date': date_to_timestamp(self.date),
                'type': 'fbsp',
                'id': self.id,
                'title': self.title,
                'text': self.text,
                'images': 
                    [i.thumbpath() for i in self.images.all() if i.thumbfile],
                }
   
class FBAd(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    date = models.DateTimeField(default=now)
    adid = models.CharField(max_length=128)
    text = models.TextField(null=True)
    title = models.TextField(null=True)
    images = models.ManyToManyField('FBAdImage', related_name='ad_images')
    links = models.ManyToManyField('FBAdLink', related_name='ad_links')
    
    def basic_data(self, anon=True):
        return {'date': date_to_timestamp(self.date),
                'id': self.id,
                'title': self.title}
                
    def detail_data(self, anon=True):
        return {'date': date_to_timestamp(self.date),
                'type': 'fbad',
                'id': self.id,
                'title': self.title,
                'text': self.text,
                'adid': self.adid,
                'images': 
                    [i.thumbpath() for i in self.images.all() if i.thumbfile],
                }
     
class FBAdLink(models.Model):
    domain = models.ForeignKey('DomainName', null=True)
    url = models.TextField(unique=True)
    localfile = models.CharField(max_length=128, null=True)
    thumbfile = models.CharField(max_length=128, null=True)
    
    def thumbpath(self):
        if self.thumbfile:
            return os.path.join(settings.VAVS_THUMBNAILS_DIR, self.thumbfile)
        else:
            return ''
    
class FBAdImage(models.Model):
    STATUS_NEW = 0
    STATUS_DONE = 1
    STATUS_ERROR = 2
    STATUS_NO_MEDIA = 3
    STATUS_HAS_MEDIA = 4
    STATUS_NO_THUMB = 5
    STATUS_NO_DOWNLOAD = 6
    STATUS_CHOICES = (
        (STATUS_NEW, 'new'),
        (STATUS_DONE, 'done'),
        (STATUS_ERROR, 'error'),
        (STATUS_NO_MEDIA, 'no media'),
        (STATUS_HAS_MEDIA, 'has media'),
        (STATUS_NO_THUMB, 'no thumb'),
        (STATUS_NO_DOWNLOAD, 'no download'),
    )
    domain = models.ForeignKey('DomainName', null=True)
    url = models.TextField(unique=True)
    localfile = models.CharField(max_length=128, null=True)
    thumbfile = models.CharField(max_length=128, null=True)
    status = models.SmallIntegerField(choices=STATUS_CHOICES,
                                    default=STATUS_NEW)
    
    def thumbpath(self):
        if self.thumbfile:
            return os.path.join(settings.VAVS_THUMBNAILS_DIR, self.thumbfile)
        else:
            return ''
        
    def status_str(self):
        return get_choice_name(self.status, self.STATUS_CHOICES)


class FBListing(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    date = models.DateTimeField(default=now)
    data = models.TextField(null=True)
    
    @property
    def listing(self):
        return json.loads(self.data) if self.data else []
    
    @listing.setter    
    def listing(self, list_data):
        self.data = json.dumps(list_data)
    
class AdRecord(models.Model):
    STATUS_NEW = 0
    STATUS_DONE = 1
    STATUS_ERROR = 2
    STATUS_NO_MEDIA = 3
    STATUS_HAS_MEDIA = 4
    STATUS_NO_THUMB = 5
    STATUS_NO_DOWNLOAD = 6
    STATUS_CHOICES = (
        (STATUS_NEW, 'new'),
        (STATUS_DONE, 'done'),
        (STATUS_ERROR, 'error'),
        (STATUS_NO_MEDIA, 'no media'),
        (STATUS_HAS_MEDIA, 'has media'),
        (STATUS_NO_THUMB, 'no thumb'),
        (STATUS_NO_DOWNLOAD, 'no download'),
    )
    TYPE_NONE = 0
    TYPE_AD = 1
    TYPE_TRACKER = 2
    TYPE_DYNAMIC = 3
    TYPE_CHOICES = (
        (TYPE_NONE, 'none'),
        (TYPE_AD, 'ad'),
        (TYPE_TRACKER, 'tracker'),
        (TYPE_DYNAMIC, 'dynamic'),
    )
    _user_id = models.PositiveIntegerField(default=0)
    date = models.DateTimeField()
    _ref_domain_id = models.PositiveIntegerField(default=0)
    _domain_id = models.PositiveIntegerField(default=0)
    url = models.TextField()
    method = models.CharField(max_length=12, null=True)
    content_type = models.CharField(max_length=64, null=True)
    cookie_url = models.TextField(null=True)
    is_ajax = models.BooleanField(default=False)
    localfile = models.CharField(max_length=128, null=True)
    thumbfile = models.CharField(max_length=128, null=True)
    status = models.SmallIntegerField(choices=STATUS_CHOICES,
                                    default=STATUS_NEW)
    ad_type = models.SmallIntegerField(choices=TYPE_CHOICES,
                                    default=TYPE_NONE)
    
    def get_user(self):
        return User.objects.get(pk=self._user_id)
    
    def get_domain(self):
        return DomainName.objects.get(pk=self._domain_id)
        
    def get_ref_domain(self):
        return DomainName.objects.get(pk=self._ref_domain_id)
        
    def thumbpath(self):
        if self.thumbfile:
            return os.path.join(settings.VAVS_THUMBNAILS_DIR, self.thumbfile)
        else:
            return ''
        
    def status_str(self):
        return get_choice_name(self.status, self.STATUS_CHOICES)
        
    def type_str(self):
        return get_choice_name(self.ad_type, self.TYPE_CHOICES)
        
    def detail_data(self, anon=True, domain=True):
        data = {'id': self.id,
                'date': date_to_timestamp(self.date),
                'type': self.ad_type}
        if domain:
            data['domain'] = self.domain.ref_name(anon=anon)
        if self.ref_domain:
            data['ref'] = self.ref_domain.ref_name(anon=anon)
        if self.thumbfile and not anon:
            data['img'] = self.thumbfile
        return data
        
    def basic_data(self, anon=True):
        data = {'id': self.id,
                'date': date_to_timestamp(self.date),
                'type': self.ad_type}
        if self.thumbfile and not anon:
            data['img'] = self.thumbfile
        return data

class AdHourlyActivity(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    date = models.DateField()
    hour = models.PositiveIntegerField(default=0)
    adtotal = models.PositiveIntegerField(default=0)
    fbadtotal = models.PositiveIntegerField(default=0)
    fbsptotal = models.PositiveIntegerField(default=0)
    fbsponsored = models.ManyToManyField('FBSponsored', 
                                related_name='ad_hour_fbsponsored')
    fbads = models.ManyToManyField('FBAd', related_name='ad_hour_fbads')
    adrecords = models.ManyToManyField('AdRecord', 
                                related_name='ad_hour_adrecords')
    
    def get_timestamp(self):
        return date_to_timestamp(datetime(self.date.year, 
                                            self.date.month, 
                                            self.date.day, 
                                            self.hour))
                                
    def packed_data(self):
        return [self.get_timestamp(), 
                    self.adtotal, self.fbadtotal, self.fbsptotal]
                                                
    def detail_data(self, anon=True):
        return {'date': date_to_timestamp(self.date),
                'hour': self.hour,
                'adtotal': self.adtotal,
                'fbadtotal': self.fbadtotal,
                'fbsptotal': self.fbsptotal}
                
    
