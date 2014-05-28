# contact.models

# DJANGO
from django.db import models

class Participate(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=128)
    email = models.CharField(max_length=128)
    
    @models.permalink
    def get_absolute_url(self):
        """
        Returns fully resolved URL for model.
        
        :rtype: unicode.
        """
        return ('participate_thankyou',)
