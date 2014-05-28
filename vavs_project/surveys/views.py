# surveys.views

# DJANGO
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.urlresolvers import reverse
from django.db.models import Max
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404
from django.views.generic.base import View, TemplateView
from django.views.generic import (
    ArchiveIndexView,
    CreateView, 
    UpdateView, 
    DetailView
)

# DJANGO-BRACES
from braces.views import LoginRequiredMixin, StaffuserRequiredMixin

# SURVEYS
from .forms import RespondentForm, SurveyForm
from .export import (
    survey_to_excel,
    survey_to_rtf
)
from .models import (
    Answer,
    Question,
    Respondent, 
    Survey
)

class ConsentView(TemplateView):
    template_name = 'surveys/consent.html'
    
    def get(self, request, pk):
        survey = get_object_or_404(Survey, pk=pk)
        form = RespondentForm(survey=survey)
        return self.render_to_response({'form':form, 'survey':survey})
        
    def post(self, request, pk=None):
        survey = get_object_or_404(Survey, pk=pk)
        form = RespondentForm(request.POST, survey=survey)
        if form.is_valid():
            survey, respondent = form.save()
            request.session['respondent'] = respondent.id
            form.send_email()
            return HttpResponseRedirect(
                            reverse('survey', kwargs={'pk':survey.id}))
        else:
            return self.render_to_response({'form':form, 'survey':survey})


@login_required
@user_passes_test(lambda u:u.is_staff, login_url='/login/')
def delete_respondent_survey_view(request, survey, respondent):
    respondent = get_object_or_404(Respondent, pk=respondent)
    survey = get_object_or_404(Survey, pk=survey)
    questions = Question.objects.filter(
                  survey=survey, display=True)
    Answer.objects.filter(
                 respondent=respondent,
                 question__in=questions).delete()
    return HttpResponseRedirect(
            reverse('survey_data', kwargs={'pk':survey.id}))
    
class SurveyView(TemplateView):
    template_name = 'surveys/survey.html'
    
    def get(self, request, pk):
        survey = get_object_or_404(Survey, pk=pk)
        try:
            respondent = Respondent.objects.get(pk=request.session['respondent'])
        except Respondent.DoesNotExist:
            return HttpResponseRedirect(
                        reverse('survey_consent', kwargs={'pk':survey.id}))
        except KeyError:
            return HttpResponseRedirect(
                        reverse('survey_consent', kwargs={'pk':survey.id}))
        form = SurveyForm(survey=survey, respondent=respondent)
        return self.render_to_response({'form':form, 'survey':survey})
        
    def post(self, request, pk):
        survey = get_object_or_404(Survey, pk=pk)
        try:
            respondent = Respondent.objects.get(pk=request.session['respondent'])
        except Respondent.DoesNotExist:
            return HttpResponseRedirect(
                        reverse('survey_consent', kwargs={'pk':survey.id}))
        except KeyError:
            return HttpResponseRedirect(
                        reverse('survey_consent', kwargs={'pk':survey.id}))
        form = SurveyForm(request.POST, survey=survey, respondent=respondent)
        if form.is_valid():
            form.save()
            form.send_email()
            del(request.session['respondent'])
            return HttpResponseRedirect(reverse('survey_thankyou'))
        else:
            return self.render_to_response({'form':form, 'survey':survey})

class RespondentIndex(StaffuserRequiredMixin, ArchiveIndexView):
    model = Respondent
    paginate_by=10
    allow_empty=True
    date_field="created"
    template_name='surveys/respondents.html' 
    
class RespondentView(LoginRequiredMixin,TemplateView):
    template_name = 'surveys/respondent.html'
    
    def get(self, request, survey, pk):
        respondent = get_object_or_404(Respondent, pk=pk)
        if request.user.is_staff or request.user.email == respondent.email:
            survey = get_object_or_404(Survey, pk=survey)
            questions = Question.objects.filter(
                         survey=survey, display=True).order_by('number')
            answers = Answer.objects.filter(
                         respondent=respondent,
                         question__in=questions).order_by('question__number')
            return self.render_to_response({
                            'survey':survey, 
                            'respondent':respondent,
                            'answers':answers})
        else:
            return HttpResponseRedirect(reverse('login')) 
    
class SurveyDataView(StaffuserRequiredMixin,TemplateView):
    template_name = 'surveys/data.html'
    
    def get(self, request, pk):
        survey = get_object_or_404(Survey, pk=pk)
        questions = Question.objects.filter(
                         survey=survey, display=True).order_by('number')
        respondents = Respondent.objects.filter(
                         survey_answers__question__survey=survey).distinct('id')
        return self.render_to_response(
                         {'survey':survey, 
                         'questions':questions,
                         'respondents':respondents})
                        
class SurveyExportData(View):
    def get(self, request, pk, to_format='excell'):
        survey = get_object_or_404(Survey, pk=pk)
        questions = Question.objects.filter(
                                survey=survey, 
                                display=True).order_by('number')
        respondents = Respondent.objects.filter(
                            survey_answers__question__survey=survey
                        ).distinct('id')
        if to_format == 'excell':
            response = HttpResponse(survey_to_excel(questions, respondents), 
                            content_type='application/vnd.ms-excel')
            response['Content-Disposition'] = 'attachment; filename="survey.xls"'
        elif to_format == 'rtf':
            response = HttpResponse(survey_to_rtf(questions, respondents), 
                            content_type='application/rtf')
            response['Content-Disposition'] = 'attachment; filename="survey.rtf"'
        else:
            raise Http404()
        return response
        
class SurveyExtractExportData(View):
    """Tmp version numbers hardcoded"""
    def get(self, request, pk, to_format='excell'):
        survey = get_object_or_404(Survey, pk=pk)
        questions = Question.objects.filter(
                                Q(number__range=(1,6))|Q(number=21),
                                survey=survey, 
                                display=True).order_by('number')
        respondents = Respondent.objects.filter(
                            survey_answers__question__survey=survey
                        ).distinct('id')
        if to_format == 'excell':
            response = HttpResponse(survey_to_excel(questions, respondents), 
                            content_type='application/vnd.ms-excel')
            response['Content-Disposition'] = 'attachment; filename="survey.xls"'
        elif to_format == 'rtf':
            response = HttpResponse(survey_to_rtf(questions, respondents), 
                            content_type='application/rtf')
            response['Content-Disposition'] = 'attachment; filename="survey.rtf"'
        else:
            raise Http404()
        return response
            
class RespondentExportData(View):
    def get(self, request, survey_id, respondent_id, to_format='excell'):
        survey = get_object_or_404(Survey, pk=survey_id)
        questions = Question.objects.filter(
                                survey=survey, 
                                display=True).order_by('number')
        respondent = get_object_or_404(Respondent, pk=respondent_id)
        if to_format == 'excell':
            response = HttpResponse(survey_to_excel(questions, [respondent]), 
                            content_type='application/vnd.ms-excel')
            response['Content-Disposition'] = 'attachment; filename="%s.xls"' % respondent.pref_name()
        elif to_format == 'rtf':
            response = HttpResponse(survey_to_rtf(questions, [respondent]), 
                            content_type='application/rtf')
            response['Content-Disposition'] = 'attachment; filename="%s.rtf"' % respondent.pref_name()
        else:
            raise Http404()
        return response
