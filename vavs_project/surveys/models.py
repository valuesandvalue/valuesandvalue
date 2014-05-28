# surveys.models

# DJANGO
from django.db import models

class Respondent(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=128)
    email = models.CharField(max_length=128, blank=True, null=True)
    pseudonym = models.CharField(max_length=128, blank=True, null=True)
    consented = models.BooleanField(default=False)
    further_contact = models.BooleanField(default=False)
    
    def pref_name(self):
        return self.pseudonym or self.name
        
class Survey(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=128, blank=True, null=True)
    
class Question(models.Model):
    survey = models.ForeignKey('Survey', related_name='questions')
    number = models.PositiveIntegerField(default=0)
    text = models.CharField(max_length=500, blank=True, null=True)
    display = models.BooleanField(default=True)
    
    def __unicode__(self):
        """
        Unicode string representation of model.

        :rtype: unicode.
        """
        return '%d. %s' % (self.number, self.text)

class Answer(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    question = models.ForeignKey('Question', related_name='answers')
    respondent = models.ForeignKey('Respondent', related_name='survey_answers')
    text = models.TextField(blank=True, null=True)
      
