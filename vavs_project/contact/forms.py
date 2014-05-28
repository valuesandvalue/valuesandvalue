# contact.forms

# DJANGO
from django import forms
from django.conf import settings
from django.contrib.sites.models import Site
from django.template.loader import render_to_string

# CRISPY
from crispy_forms.helper import FormHelper
from crispy_forms.layout import (
    Layout, 
    Field,
    Fieldset, 
    ButtonHolder, 
    Submit, 
    Div
)

# UTILS
from utils.comms import send_html_mail

# CONTACT
from .models import Participate

class ContactForm(forms.Form):
    name = forms.CharField(required=True, max_length=240, label='Name:')
    email = forms.CharField(required=False, max_length=240, label='Email:')
    message = forms.CharField(
                    required=True, 
                    label='Message:', 
                    widget=forms.Textarea(attrs={'rows':6, 'cols':40}))
                    
    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_class = 'vavs-form'
        self.helper.layout = Layout(
            Fieldset(
                '',
                Div(Field('name', css_class="inline-element"),
                    css_class="inline-elements"),
                Div(Field('email', css_class="inline-element"), 
                    css_class="inline-elements"),
                Field('message', css_class="wide-thin-area"),
            ),
            ButtonHolder(
                Submit('submit', 'Submit', css_class='button white push-down-24')
            )
        )
        super(ContactForm, self).__init__(*args, **kwargs)
        
    def send_email(self):
        site_domain = Site.objects.get_current().domain
        name = self.cleaned_data['name']
        email = self.cleaned_data.get('email', None)
        message = self.cleaned_data['message']
        # admin
        subject = 'Message to Values & Value.'
        content_plain = render_to_string(
                'emails/message_received.txt',
                {'name': name,
                'email':email,
                'message': message})
        content_html = render_to_string(
                'emails/message_received.html',
                {'name': name,
                'email':email,
                'title':subject,
                'message': message,
                'site':site_domain})
        send_html_mail(subject, 
                content_plain, 
                content_html, 
                settings.VAVS_EMAIL_TO)
        # sender
        if email:
            subject = 'Your message to Values & Value.'
            content_plain = render_to_string(
                    'emails/message_confirmed.txt',
                    {'name': name,
                    'email':email,
                    'message': message})
            content_html = render_to_string(
                    'emails/message_confirmed.html',
                    {'name': name,
                    'email':email,
                    'title':subject,
                    'message': message,
                    'site':site_domain})
            send_html_mail(subject, content_plain, content_html, [email])   
    
class ParticipateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_class = 'vavs-form'
        self.helper.layout = Layout(
            Fieldset(
                '',
                Div(Field('name', css_class="inline-element"),
                    css_class="inline-elements"),
                Div(Field('email', css_class="inline-element"), 
                    css_class="inline-elements"),
            ),
            ButtonHolder(
                Submit('submit', 'Submit', css_class='button white push-down-24')
            )
        )
        super(ParticipateForm, self).__init__(*args, **kwargs)
        
    def send_email(self):
        email = self.cleaned_data['email']
        if email:
            subject = 'Participating in Values & Value.'
            site_domain = Site.objects.get_current().domain
            content_plain = render_to_string(
                    'emails/participation_confirmed.txt',
                    {'name': self.cleaned_data['name']})
            content_html = render_to_string(
                    'emails/participation_confirmed.html',
                    {'name': self.cleaned_data['name'],
                    'title':subject,
                    'site':site_domain})
            send_html_mail(subject, content_plain, content_html, [email])
        
    class Meta:
        model = Participate
        
