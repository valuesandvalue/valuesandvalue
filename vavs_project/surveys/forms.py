# surveys.forms

# DJANGO
from django import forms
from django.conf import settings
from django.contrib.sites.models import Site
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string

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

# UTILS
from utils.comms import send_html_mail

# COMMENT
from .models import Survey, Respondent, Question, Answer

class RespondentForm(forms.ModelForm):
    survey = forms.IntegerField(required=True, widget=forms.HiddenInput)
    captcha = CaptchaField()
    consented = forms.BooleanField(required=True)
    
    def __init__(self, *args, **kwargs):
        survey = kwargs.pop('survey')
        self.helper = FormHelper()
        self.helper.form_class = 'vavs-form'
        self.helper.error_text_inline = False
        self.helper.layout = Layout(
            Fieldset(
                '',
                Div(Field('consented', css_class="inline-element"),
                    css_class="inline-elements"),
                Div(Field('further_contact', css_class="inline-element"),
                    css_class="inline-elements"),
                Div(Field('name', css_class="inline-element"),
                    css_class="inline-elements"),
                Div(Field('pseudonym', css_class="inline-element"),
                    css_class="inline-elements"),
                Div(Field('email', css_class="inline-element"), 
                    css_class="inline-elements"),
                Div(Field('captcha', css_class="captcha-input"),
                    HTML("<p class=\"captcha-help\">Click on the image to change the security word.</p>"),
                    css_class="captcha-controls"),
            ),
            Field('survey'),
            ButtonHolder(
                Submit('submit', 'Submit', css_class='button white push-down-24')
            )
        )
        super(RespondentForm, self).__init__(*args, **kwargs)
        self.fields['survey'].initial = survey.id
        self.fields['consented'].label = 'I have read the above agreement and give my consent to be included in the project.'
        self.fields['further_contact'].label = 'Please send me updates on the research and possible further involvement.'
        self.fields['name'].label = 'Name:'
        self.fields['pseudonym'].label = 'Pseudonym (optional):'
        self.fields['email'].label = 'Email:'
        self.fields['captcha'].label = 'To prevent spam, pease enter the text you see in the image below:'
        
    def save(self):
        self._survey = get_object_or_404(Survey, pk=self.cleaned_data['survey'])
        self._respondent = super(RespondentForm, self).save() 
        return (self._survey, self._respondent)
        
    def send_email(self):
        site_domain = Site.objects.get_current().domain
        name = self._respondent.name
        email = self._respondent.email
        # admin
        subject = 'Consent to participate in Values and Value project'
        content_plain = render_to_string(
                'emails/new_respondent.txt',
                {'respondent': self._respondent})
        content_html = render_to_string(
                'emails/new_respondent.html',
                {'respondent': self._respondent,
                'title':subject,
                'site':site_domain})
        send_html_mail(subject, 
                content_plain, 
                content_html, 
                settings.VAVS_EMAIL_SURVEYS)
        # sender
        if email:
            content_plain = render_to_string(
                    'emails/respondent_consent.txt',
                    {'respondent': self._respondent})
            content_html = render_to_string(
                    'emails/respondent_consent.html',
                    {'respondent': self._respondent,
                    'title':subject,
                    'site':site_domain})
            send_html_mail(subject, content_plain, content_html, [email])
        
    class Meta:
        model = Respondent
        fields = ('consented', 'further_contact', 'name', 'pseudonym', 'email')

class SurveyForm(forms.Form):
    survey = forms.IntegerField(required=True, widget=forms.HiddenInput)
    respondent = forms.IntegerField(required=True, widget=forms.HiddenInput)
    
    def __init__(self, *args, **kwargs):
        survey = kwargs.pop('survey')
        respondent = kwargs.pop('respondent')
        questions = survey.questions.filter(display=True).order_by('number')
        self.helper = FormHelper()
        self.helper.form_class = 'vavs-form'
        self.helper.error_text_inline = False
        qfields = [Field(str(question.id), css_class="wide-thin-area") 
                    for question in questions]
        qfields.append(Field('survey'))
        qfields.append(Field('respondent'))
        qfields.append(
            ButtonHolder(
                Submit('submit', 'Submit', 
                    css_class='button white push-down-24')
            )
        )
        self.helper.layout = Layout(*qfields)
        super(SurveyForm, self).__init__(*args, **kwargs)
        self.fields['survey'].initial = survey.id
        self.fields['respondent'].initial = respondent.id
        for question in questions:
            self.fields[str(question.id)] = forms.CharField(
                                    label=unicode(question), 
                                    required=False,
                                    widget=forms.Textarea) 
                          
    def save(self):
        answers = self.cleaned_data
        self._survey = get_object_or_404(Survey, pk=answers.pop('survey'))
        self._respondent = get_object_or_404(Respondent, 
                                    pk=answers.pop('respondent'))
        self._answers = []
        for key, value in answers.items():
            if value:
                question = get_object_or_404(Question, pk=int(key))
                answer, created = Answer.objects.get_or_create(
                                    question=question,
                                    respondent=self._respondent)
                answer.text = value
                answer.save()
                self._answers.append(answer)
        self._answers.sort(key=lambda arg: arg.question.number)
    
    def send_email(self):
        if self._answers:
            site_domain = Site.objects.get_current().domain
            subject = 'Survey response: %s' % self._survey.name
            email = self._respondent.email
            # admin
            content_plain = render_to_string(
                    'emails/survey_result.txt',
                    {'respondent': self._respondent,
                    'answers':self._answers})
            content_html = render_to_string(
                    'emails/survey_result.html',
                    {'respondent': self._respondent,
                    'answers':self._answers,
                    'title':subject,
                    'site':site_domain})
            send_html_mail(subject, 
                    content_plain, 
                    content_html, 
                    settings.VAVS_EMAIL_SURVEYS)
            # sender
            if email:
                content_plain = render_to_string(
                        'emails/survey_respondent.txt',
                        {'respondent': self._respondent,
                        'answers':self._answers})
                content_html = render_to_string(
                        'emails/survey_respondent.html',
                        {'respondent': self._respondent,
                        'answers':self._answers,
                        'title':subject,
                        'site':site_domain})
                send_html_mail(subject, content_plain, content_html, [email])
        
        
