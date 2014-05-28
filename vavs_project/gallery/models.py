# gallery.models

# DJANGO
from django.db import models

class ImageFile(models.Model):
    image = models.ImageField(upload_to="gallery", 
                height_field="height", width_field="width")
    caption = models.CharField(max_length=256, blank=True, null=True)
    height = models.PositiveIntegerField(null=True, 
                blank=True, editable=False, default="100")
    width = models.PositiveIntegerField(null=True, 
                blank=True, editable=False, default="100")
                
    @models.permalink
    def get_absolute_url(self):
        """
        Returns fully resolved URL for model.
        
        :rtype: unicode.
        """
        return ('gallery_image', (), {'pk':self.id})
