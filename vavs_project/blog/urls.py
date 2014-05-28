# blog.urls

# DJANGO
from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView, ListView
from django.views.generic.dates import ArchiveIndexView

# BLOG
from .rssfeeds import LatestBlogFeed
from .models import BlogItem, Theme
from .views import (
    blog_category_view,
    BlogItemDetailView, 
    BlogItemCreateView, 
    BlogItemUpdateView,
    ThemeCreateView, 
    ThemeDetailView, 
    ThemeUpdateView,
    FrontPageView
)

blog_archive_view = ArchiveIndexView.as_view(
                queryset=BlogItem.objects.filter(display=True),
                paginate_by=10, 
                allow_empty=True,
                date_field="created",
                template_name='blog/index.html')
                
theme_list_view = ListView.as_view(
                queryset=Theme.objects.filter(display=True),
                paginate_by=10, 
                template_name='themes/index.html')

urlpatterns = patterns('',
    # blog feed
    (r'^feed/$', LatestBlogFeed()),
    # blog categories
    url(r'^blog/category/(?P<slug>\w+)/$', view=blog_category_view,
                name='blog_category'),
    url(r'^blog/category/(?P<slug>\w+)/page/(?P<page>\d+)/$', view=blog_category_view,
            name='blog_category_paginated'),
    # blog items
    url(r'^blog/create/$',     
            view=BlogItemCreateView.as_view(), name='create_blog_item'),
    url(r'^blog/(?P<pk>\d+)/$',     
            view=BlogItemDetailView.as_view(), name='blog_item'),
    url(r'^blog/update/(?P<pk>\d+)/$',     
            view=BlogItemUpdateView.as_view(), name='update_blog_item'),
    url(r'^blog/$', view=blog_archive_view, name='current_blog'),
    url(r'^blog/page/(?P<page>\d+)/$', view=blog_archive_view,
            name='current_blog_paginated'),
    # themes
    url(r'^theme/create/$',     
            view=ThemeCreateView.as_view(), name='create_theme'),
    url(r'^theme/(?P<pk>\d+)/$',     
            view=ThemeDetailView.as_view(), name='theme'),
    url(r'^theme/update/(?P<pk>\d+)/$',     
            view=ThemeUpdateView.as_view(), name='update_theme'),
    url(r'^themes/$', view=theme_list_view, name='theme_index'),
    url(r'^themes/page/(?P<page>\d+)/$', view=theme_list_view,
            name='theme_index_paginated'),
    # front
    url(r'^$', FrontPageView.as_view()),
)
