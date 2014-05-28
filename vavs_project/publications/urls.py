# publications.urls

# DJANGO
from django.conf.urls import patterns, include, url
from django.views.generic import ListView

# NEWS
from .models import Publication
from .views import (
    PublicationDetailView, 
    PublicationCreateView,
    PublicationUpdateView
)

publications_list_view = ListView.as_view(
                model=Publication,
                paginate_by=10, 
                template_name='publications/index.html')
                
urlpatterns = patterns('',
    url(r'^add/$',     
            view=PublicationCreateView.as_view(), name='add_publication'),
    url(r'^(?P<pk>\d+)/$',     
            view=PublicationDetailView.as_view(), name='publication'),
    url(r'^update/(?P<pk>\d+)/$',     
            view=PublicationUpdateView.as_view(), name='update_publication'),
    url(r'^$', view=publications_list_view, name='publications_index'),
    url(r'^page/(?P<page>\d+)/$', view=publications_list_view,
            name='publications_index_paginated'),
)
