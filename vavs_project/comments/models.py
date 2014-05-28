# comments.models

# DJANGO
from django.db import models

class Comment(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=128, blank=True, null=True)
    email = models.CharField(max_length=128, blank=True, null=True)
    influenced = models.TextField(blank=True, null=True)
    types = models.TextField(blank=True, null=True)
    question_1 = models.TextField(blank=True, null=True)
    question_2 = models.TextField(blank=True, null=True)
    question_3 = models.TextField(blank=True, null=True)
    display = models.BooleanField(default=True)
    
    @models.permalink
    def get_absolute_url(self):
        """
        Returns fully resolved URL for model.
        
        :rtype: unicode.
        """
        return ('comment', (), {'pk':self.id})
        
