# feeds.forms

# DJANGO
from django import forms
from crispy_forms.layout import Submit

# CRISPY
from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Fieldset, Div, Submit, Reset

# FEEDS
from .models import ExternalFeed, PageLink

class ExternalFeedForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_id = 'id-form'
        self.helper.form_class = 'form-horizontal '
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Fieldset(
                '',
                Div(
                    'category', 
                    'name',
                    css_id = 'name-fields'
                ),
                'url', 
                'site', 
                'description', 
                'tags',
                'active'
            ),
            FormActions(
                Submit('save', 'Create'),
                Reset('reset', 'Clear')
            )
        )
        super(ExternalFeedForm, self).__init__(*args, **kwargs)
        
    class Meta:
        model = ExternalFeed
        fields = ('category',
                'name', 
                'active', 
                'url', 
                'site', 
                'description', 
                'tags')
        
class PageLinkForm(forms.ModelForm):
    class Meta:
        model = PageLink
        fields = ('category', 'name', 'active', 'url', 'description', 'tags')
