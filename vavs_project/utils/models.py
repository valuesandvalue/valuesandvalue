# utils.models

# DJANGO
from django.db import models

class IndexSlice(models.Model):
    name = models.CharField(max_length=64, unique=True)
    index = models.PositiveIntegerField(default=0)
    
    def update_index(self, value, limit=None):
        value = self.index + value
        if limit and value >= limit:
            value = 0
        self.index = value
        
