# feeds.urls

# DJANGO
from django.conf.urls import patterns, include, url
from django.views.generic import ListView

# NEWS
from .models import ImageFile
from .views import (
    ImageFileDetailView, 
    ImageFileCreateView,
    ImageFileUpdateView,
    ImageFileListView
)

urlpatterns = patterns('',
    url(r'^add/$',     
            view=ImageFileCreateView.as_view(), name='add_gallery_image'),
    url(r'^(?P<pk>\d+)/$',     
            view=ImageFileDetailView.as_view(), name='gallery_image'),
    url(r'^update/(?P<pk>\d+)/$',     
            view=ImageFileUpdateView.as_view(), name='update_gallery_image'),
    url(r'^$', view=ImageFileListView.as_view(), name='gallery_index'),
    url(r'^page/(?P<page>\d+)/$', view=ImageFileListView.as_view(),
            name='gallery_index_paginated'),
)
