# publications.models

# DJANGO
from django.db import models

# TAGGIT
from taggit.managers import TaggableManager

class Publication(models.Model):
    pubfile = models.FileField(upload_to="publications")
    title = models.CharField(max_length=256)
    published = models.DateTimeField(blank=True, null=True)
    display = models.BooleanField(default=True)
    authors = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    category = models.CharField(max_length=64, blank=True, null=True)
    tags = TaggableManager(blank=True)
                
    @models.permalink
    def get_absolute_url(self):
        """
        Returns fully resolved URL for model.
        
        :rtype: unicode.
        """
        return ('publication', (), {'pk':self.id})
