# gallery.forms

# DJANGO
from django import forms

# FEEDS
from .models import ImageFile

class ImageFileForm(forms.ModelForm):
    class Meta:
        model = ImageFile
        fields = ('image', 'caption')
