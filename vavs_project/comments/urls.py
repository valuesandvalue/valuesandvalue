# comments.urls

# DJANGO
from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView, ListView
from django.views.generic.dates import ArchiveIndexView

# COMMENTS
from .models import Comment
from .views import (
    comment_archive_view,
    delete_comment_view,
    CommentDetailView, 
    CommentCreateView, 
    CommentUpdateView,
)
            
urlpatterns = patterns('',
    # comment items
    url(r'^create/$',     
            view=CommentCreateView.as_view(), name='create_comment'),
    url(r'^(?P<pk>\d+)/$',     
            view=CommentDetailView.as_view(), name='comment'),
    url(r'^update/(?P<pk>\d+)/$',     
            view=CommentUpdateView.as_view(), name='update_comment'),
    url(r'^delete/(?P<pk>\d+)/$',     
            view=delete_comment_view, name='delete_comment'),
    url(r'^$', view=comment_archive_view, name='current_comments'),
    url(r'^page/(?P<page>\d+)/$', view=comment_archive_view,
            name='current_comments_paginated'),
)
