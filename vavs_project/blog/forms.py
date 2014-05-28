# blog.forms

# DJANGO
from django import forms

# CRISPY
from crispy_forms.helper import FormHelper
from crispy_forms.layout import (
    Layout, 
    Field,
    Fieldset, 
    Button,
    ButtonHolder, 
    Submit, 
    Div,
    HTML
)

# BLOG
from .models import BlogItem, Theme

class BlogItemForm(forms.ModelForm):
    display_date = forms.DateField(required=False)
    
    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_class = 'vavs-form'
        self.helper.error_text_inline = False
        self.helper.layout = Layout(
            Fieldset(
                '',
                Div(Field('category')),
                Div(Field('title', css_class="inline-element"), 
                    css_class="inline-elements"),
                Div(Field('display_date', css_class="inline-element"),
                    css_class="inline-elements"),
                Div(Field('display', css_class="inline-element"),
                    css_class="inline-elements"),
                Field('bodyraw', css_class="wide-thin-area"),
                Div(Field('tags', css_class="inline-element"),
                    css_class="inline-elements"),
            ),
            ButtonHolder(
                Submit('submit', 'Submit', css_class='button white push-down-24')
            )
        )
        super(BlogItemForm, self).__init__(*args, **kwargs)
        self.fields['category'].label = 'Category:'
        self.fields['title'].label = 'Title:'
        self.fields['display_date'].label = 'Date for an event DD/MM/YYYY (optional):'
        self.fields['display'].label = 'Display posting:'
        self.fields['bodyraw'].label = 'Content:'
        self.fields['tags'].label = 'Tags (optional):'
        
    class Meta:
        model = BlogItem
        fields = ('category', 
            'title', 'display_date', 'display', 'bodyraw', 'tags')
        
class ThemeForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_class = 'vavs-form'
        self.helper.error_text_inline = False
        self.helper.layout = Layout(
            Fieldset(
                '',
                Div(Field('name', css_class="inline-element"),
                    css_class="inline-elements"),
                Div(Field('display', css_class="inline-element"),
                    css_class="inline-elements"),
                Field('bodyraw', css_class="wide-thin-area"),
            ),
            ButtonHolder(
                Submit('submit', 'Submit', css_class='button white push-down-24')
            )
        )
        super(ThemeForm, self).__init__(*args, **kwargs)
        self.fields['name'].label = 'Name:'
        self.fields['display'].label = 'Display theme:'
        self.fields['bodyraw'].label = 'Content:'
        
    class Meta:
        model = Theme
        fields = ('name', 'display', 'bodyraw')
