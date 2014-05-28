# vavs_project.urls

# DJANGO
from django.conf import settings
from django.conf.urls import patterns, include, url, static
from django.views.generic import TemplateView

# API
from addata.api import get_api

urlpatterns = patterns('',
    # api
    url(r'^api/', include(get_api().urls)),
    # addata
    url(r'^admonitor/', include('addata.urls')),
    # captcha
    url(r'^captcha/', include('captcha.urls')),
    # comments
    url(r'^comments/', include('comments.urls')),
    # surveys
    url(r'^survey/', include('surveys.urls')),
    # about
    url(r'^about/people/$', 
            TemplateView.as_view(template_name='flatpages/profiles.html')),
    url(r'^about/$', 
            TemplateView.as_view(template_name='flatpages/about.html')),
    # facebook
    (r'^facebook/', include('django_facebook.urls')),
    # facebook analysis
    url(r'^analysis/', include('fbdata.urls')),
    # facebook interactions
    url(r'^interactions/$', 
            TemplateView.as_view(
                template_name='flatpages/interactions_study.html'),
                name='interactions_study'),
    # privacy policy
    url(r'^privacy/$', 
            TemplateView.as_view(
                template_name='flatpages/privacy_policy.html'),
                name='privacy_policy'),
    # testers
    url(r'^testers/$', 
            TemplateView.as_view(
                template_name='flatpages/testers.html'),
                name='testers'),
    # reading
    url(r'^resources/reading/$', 
            TemplateView.as_view(template_name='flatpages/reading.html')),
    # gallery
    url(r'^gallery/', include('gallery.urls')),
    # publications
    url(r'^resources/publications/', include('publications.urls')),
    # accounts
    url(r'^accounts/', include('accounts.urls')),
    # external feeds
    url(r'^resources/', include('feeds.urls')),
    # contact and participate
    url(r'^', include('contact.urls')),
    # blog
    url(r'^', include('blog.urls')),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
    )
