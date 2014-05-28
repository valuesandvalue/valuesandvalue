# blog.models

# DJANGO
from django.db import models

# MARKDOWN
import markdown

# TAGGIT
from taggit.managers import TaggableManager

############
# UTILS
############
def _raw_to_html(raw):
    """Converts raw markdown to HTML."""
    return markdown.markdown(raw, safe_mode='escape')

############
# CLASSES
############
class BlogCategory(models.Model):
    name = models.CharField(max_length=64, unique=True)
    slug = models.CharField(max_length=64, unique=True)
    
    def __unicode__(self):
        """
        Unicode string representation of model.

        :rtype: unicode.
        """
        return self.name
    
    @models.permalink
    def get_absolute_url(self):
        """
        Returns fully resolved URL for model.
        
        :rtype: unicode.
        """
        return ('blog_category', (), {'slug':self.slug})

class BlogItem(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=128)
    display = models.BooleanField(default=True)
    bodyraw = models.TextField(blank=True, null=True)
    bodyhtml = models.TextField(blank=True, null=True)
    category = models.ForeignKey(
                'BlogCategory', related_name='blog_items', null=True)
    tags = TaggableManager(blank=True)
    display_date = models.DateField(null=True)
    
    @models.permalink
    def get_absolute_url(self):
        """
        Returns fully resolved URL for model.
        
        :rtype: unicode.
        """
        return ('blog_item', (), {'pk':self.id})
        
    def save(self, *args, **kwargs):
        """Overrides save to create html from markdown."""
        self.bodyhtml = _raw_to_html(self.bodyraw)
        if not self.is_event():
            self.display_date = None
        super(BlogItem, self).save(*args, **kwargs)
        
    def is_event(self):
        """Returns True if blog item is an event."""
        return self.category and self.category.name == 'Events'
        

class Theme(models.Model):
    name = models.CharField(max_length=128)
    display = models.BooleanField(default=True)
    bodyraw = models.TextField(blank=True, null=True)
    bodyhtml = models.TextField(blank=True, null=True)
    
    def save(self, *args, **kwargs):
        """Overrides save to create html from markdown."""
        self.bodyhtml = _raw_to_html(self.bodyraw)
        super(Theme, self).save(*args, **kwargs)
        
    @models.permalink
    def get_absolute_url(self):
        """
        Returns fully resolved URL for model.
        
        :rtype: unicode.
        """
        return ('theme', (), {'pk':self.id})
        
        
