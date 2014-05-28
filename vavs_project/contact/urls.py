# contact.urls

# DJANGO
from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView

# COMMENTS
from .models import Participate
from .views import (
    ContactView,
    participant_list_view,
    delete_participant_view,
    ParticipateDetailView, 
    ParticipateCreateView, 
    ParticipateUpdateView
)
            
urlpatterns = patterns('',
    # contact
    url(r'^contact/$', view=ContactView.as_view(), name='contact'),
    url(r'^contact/thankyou/$',     
            view=TemplateView.as_view(
                template_name='contact/contact_thankyou.html'), 
                name='contact_thankyou'),
    # interest
    url(r'^participate/$',     
            view=ParticipateCreateView.as_view(), name='participate'),
    url(r'^participate/thankyou/$',     
            view=TemplateView.as_view(
                template_name='contact/participate_thankyou.html'), 
                name='participate_thankyou'),
    url(r'^participants/(?P<pk>\d+)/$',     
            view=ParticipateDetailView.as_view(), name='interest'),
    url(r'^participants/update/(?P<pk>\d+)/$',     
            view=ParticipateUpdateView.as_view(), name='update_participant'),
    url(r'^participants/delete/(?P<pk>\d+)/$',     
            view=delete_participant_view, name='delete_participant'),
    url(r'^participants/$', view=participant_list_view, name='participant_index'),
    url(r'^participants/page/(?P<page>\d+)/$', view=participant_list_view,
            name='participant_index_paginated'),
)
