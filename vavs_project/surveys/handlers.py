# surveys.handlers

# DJANGO
from django.db.models import F

# SURVEYS
from .models import (
    Answer,
    Question,
    Respondent
)

def insert_question(survey, number, text, display=True):
    Question.objects.filter(
            survey=survey, 
            number__gte=number, 
            display=True).update(number=F('number')+1)
    return Question.objects.create(
                survey=survey, number=number, text=text, display=display)
                
def get_answers_for_email(survey, email):
    return Answer.objects.filter(
                 respondent__email=email,
                 question__survey=survey
             ).prefetch_related('question').order_by('question__number')
    
