# accounts.forms

# DJANGO
from django import forms
from django.contrib import auth

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

# ACCOUNTS
from .models import StaffProfile

class LoginForm(forms.Form):
    name = forms.CharField(required=True, max_length=64, label='Name:')
    password = forms.CharField(
                        required=True, 
                        max_length=64, 
                        label='Password:', 
                        widget=forms.PasswordInput)
                    
    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_class = 'vavs-form'
        self.helper.error_text_inline = False
        self.helper.layout = Layout(
            Fieldset(
                '',
                Div(Field('name', css_class="inline-element"),
                    css_class="inline-elements"),
                Div(Field('password', css_class="inline-element"), 
                    css_class="inline-elements"),
            ),
            ButtonHolder(
                Submit('submit', 'Login', 
                    css_class='button white push-down-24')
            )
        )
        super(LoginForm, self).__init__(*args, **kwargs)
        
    def login(self, request):
        user = auth.authenticate(
                username=self.cleaned_data['name'], 
                password=self.cleaned_data['password'])
        if user and user.is_active:
            auth.login(request, user)
            return True
        else:
            return False


class StaffProfileForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_class = 'vavs-form'
        self.helper.error_text_inline = False
        self.helper.layout = Layout(
            Div(Field('email_feeds')),
            ButtonHolder(
                Submit('submit', 'Update', css_class='button white push-down-24')
            )
        )
        super(StaffProfileForm, self).__init__(*args, **kwargs)
        self.fields['email_feeds'].label = 'Email feed summaries.'
        
    class Meta:
        model = StaffProfile
        fields = ('email_feeds',)    
        
class ConsentForm(forms.Form):
    consented = forms.BooleanField(required=True)
    
    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_class = 'vavs-form'
        self.helper.error_text_inline = False
        self.helper.layout = Layout(
            Fieldset(
                '',
                Div(Field('consented', css_class="inline-element"),
                    css_class="inline-elements"),
            ),
            Field('survey'),
            ButtonHolder(
                Submit('submit', 'Submit', css_class='button white push-down-24')
            )
        )
        super(ConsentForm, self).__init__(*args, **kwargs)
        self.fields['consented'].label = 'I have read the above agreement and give my consent to be included in the project.'
        
