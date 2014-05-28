# comments.forms

# DJANGO
from django import forms

# CAPTCHA
from captcha.fields import CaptchaField

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

# COMMENT
from .models import Comment

class CommentForm(forms.ModelForm):
    captcha = CaptchaField()
    
    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_class = 'vavs-form'
        self.helper.error_text_inline = False
        self.helper.layout = Layout(
            Fieldset(
                '',
                Field('question_1', css_class="wide-thin-area"),
                Field('question_2', css_class="wide-thin-area"),
                Field('question_3', css_class="wide-thin-area"),
                Div(Field('name', css_class="inline-element"),
                    css_class="inline-elements"),
                Div(Field('email', css_class="inline-element"), 
                    css_class="inline-elements"),
                Div(Field('captcha', css_class="captcha-input"),
                    HTML("<p class=\"captcha-help\">Click on the image to change the security word.</p>"),
                    css_class="captcha-controls"),
                Div(Field('display', css_class="inline-element"),
                    css_class="inline-elements"),
            ),
            ButtonHolder(
                Submit('submit', 'Submit', css_class='button white push-down-24')
            )
        )
        super(CommentForm, self).__init__(*args, **kwargs)
        self.fields['question_1'].label = 'How has Facebook influenced your friendships and how you interact with people?'
        self.fields['question_2'].label = 'What do like or dislike about Facebook?'
        self.fields['question_3'].label = 'How central is Facebook to your life?'
        self.fields['name'].label = 'Name (optional):'
        self.fields['email'].label = 'Email (optional):'
        self.fields['display'].label = 'Allow my comment to be public - your name and email will not be shown.'
        self.fields['captcha'].label = 'To prevent spam, pease enter the text you see in the image below:'
        
    class Meta:
        model = Comment
        fields = ('question_1', 'question_2', 'question_3', 'name', 'email', 'display')
