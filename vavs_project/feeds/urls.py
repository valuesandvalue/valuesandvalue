# feeds.urls

# DJANGO
from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView, ListView
from django.views.generic.dates import ArchiveIndexView

# NEWS
from .models import ExternalFeed, PageLink
from .views import (
    ExternalFeedDetailView, 
    ExternalFeedCreateView,
    ExternalFeedUpdateView,
    PageLinkCreateView, 
    PageLinkUpdateView
)

feed_list_names_view = ListView.as_view(
                model=ExternalFeed,
                queryset=ExternalFeed.objects.filter(
                            active=True).order_by('name'),
                paginate_by=10, 
                template_name='feeds/current.html')
                
feed_list_recent_view = ListView.as_view(
                model=ExternalFeed,
                queryset=ExternalFeed.objects.filter(active=True, 
                    updated__isnull=False).order_by('-updated'),
                paginate_by=10, 
                template_name='feeds/current.html')

link_list_view = ListView.as_view(
                model=PageLink,
                paginate_by=10, 
                queryset=PageLink.objects.filter(active=True).order_by('name'),
                template_name='links/current.html')
               
urlpatterns = patterns('',
    # feeds
    url(r'^feeds/create/$',     
            view=ExternalFeedCreateView.as_view(), name='create_external_feed'),
    url(r'^feeds/(?P<pk>\d+)/$',     
            view=ExternalFeedDetailView.as_view(), name='external_feed'),
    url(r'^feeds/update/(?P<pk>\d+)/$',     
            view=ExternalFeedUpdateView.as_view(), name='update_external_feed'),
    url(r'^feeds/$', view=feed_list_names_view, name='current_feeds'),
    url(r'^feeds/page/(?P<page>\d+)/$', view=feed_list_names_view,
            name='current_feeds_paginated'),
    # links
    url(r'^links/create/$',     
            view=PageLinkCreateView.as_view(), name='create_page_link'),
    url(r'^links/update/(?P<pk>\d+)/$',     
            view=PageLinkUpdateView.as_view(), name='update_page_link'),
    url(r'^links/$', view=link_list_view, name='page_links'),
    url(r'^links/page/(?P<page>\d+)/$', view=link_list_view,
            name='page_links_paginated'),
)
