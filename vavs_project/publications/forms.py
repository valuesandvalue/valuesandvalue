# publications.forms

# DJANGO
from django import forms

# FEEDS
from .models import Publication

class PublicationForm(forms.ModelForm):
    class Meta:
        model = Publication
        fields = ('pubfile',
                'title',
                'published',
                'display',
                'authors',
                'description',
                'category',
                'tags')
