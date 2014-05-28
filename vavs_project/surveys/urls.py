# surveys.urls

# DJANGO
from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView, ListView
from django.views.generic.dates import ArchiveIndexView

# SURVEYS
from .views import (
    ConsentView,
    delete_respondent_survey_view,
    RespondentView,
    RespondentIndex,
    RespondentExportData,
    SurveyView,
    SurveyDataView,
    SurveyExportData,
    SurveyExtractExportData
)
            
urlpatterns = patterns('',
    url(r'^thankyou/$', 
            TemplateView.as_view(template_name='surveys/thankyou.html'),
            name='survey_thankyou'),
    url(r'^consent/(?P<pk>\d+)/$',     
            view=ConsentView.as_view(), name='survey_consent'),
    url(r'^respondent/(?P<survey>\d+)/(?P<pk>\d+)/$',     
            view=RespondentView.as_view(), name='respondent'),
    url(r'^respondent/delete/(?P<survey>\d+)/(?P<respondent>\d+)/$',     
            view=delete_respondent_survey_view, 
            name='delete_respondent_survey'),
    url(r'^(?P<pk>\d+)/$',     
            view=SurveyView.as_view(), name='survey'),
    url(r'^data/(?P<pk>\d+)/$',     
            view=SurveyDataView.as_view(), name='survey_data'),
    url(r'^data/extract/excell/(?P<pk>\d+)/$',     
            view=SurveyExtractExportData.as_view(), 
            kwargs={'to_format':'excell'}, name='survey_extract_excell'),
    url(r'^data/extract/rtf/(?P<pk>\d+)/$',     
            view=SurveyExtractExportData.as_view(), 
            kwargs={'to_format':'rtf'}, name='survey_extract_rtf'),
    url(r'^data/excell/(?P<pk>\d+)/$',     
            view=SurveyExportData.as_view(), 
            kwargs={'to_format':'excell'}, name='survey_excell'),
    url(r'^data/rtf/(?P<pk>\d+)/$',     
            view=SurveyExportData.as_view(), 
            kwargs={'to_format':'rtf'}, name='survey_rtf'),
    url(r'^data/respondent/excell/(?P<survey_id>\d+)/(?P<respondent_id>\d+)/$',     
            view=RespondentExportData.as_view(), 
            kwargs={'to_format':'excell'}, name='respondent_excell'),
    url(r'^data/respondent/rtf/(?P<survey_id>\d+)/(?P<respondent_id>\d+)/$',     
            view=RespondentExportData.as_view(),
            kwargs={'to_format':'rtf'}, name='respondent_rtf'),
    # default survey
    url(r'^$', view=SurveyView.as_view(), kwargs={'pk':1}),
)
