# feeds.models

# DJANGO
from django.db import models

# TAGGIT
from taggit.managers import TaggableManager

class ExternalFeed(models.Model):
    name = models.CharField(max_length=128)
    active = models.BooleanField(default=True)
    url = models.URLField()
    site = models.URLField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    category = models.CharField(max_length=64, blank=True, null=True)
    tags = TaggableManager(blank=True)
    updated = models.DateTimeField(blank=True, null=True)
    
    @models.permalink
    def get_absolute_url(self):
        """
        Returns fully resolved URL for model.
        
        :rtype: unicode.
        """
        return ('external_feed', (), {'pk':self.id})
        
    def recent_entries(self):
        """Returns 6 most recent entries in feed."""
        return FeedEntry.objects.filter(feed=self).order_by('-published')[0:6]
        
class FeedEntry(models.Model):
    feed = models.ForeignKey('ExternalFeed', related_name='entries')
    title = models.CharField(max_length=256, blank=True, null=True)
    published = models.DateTimeField()
    summary = models.TextField(blank=True, null=True)
    link = models.URLField(blank=True, null=True)
    
class PageLink(models.Model):
    name = models.CharField(max_length=128)
    active = models.BooleanField(default=True)
    url = models.URLField()
    description = models.TextField(blank=True, null=True)
    category = models.CharField(max_length=64, blank=True, null=True)
    tags = TaggableManager(blank=True)
    
