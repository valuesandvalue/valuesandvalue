# fbdata.urls

# DJANGO
from django.conf.urls import patterns, include, url
from django.views.decorators.cache import cache_page

# FBDATA
from .views import (
    UserAnalysisView,
    InteractionData,
    DetailData
)

_CACH_TIMEOUT = 60 * 60
            
urlpatterns = patterns('',
    url(r'^(?P<username>\w+)/(?P<start>[\d\-]+)/(?P<end>[\d\-]+)/$', 
        view=UserAnalysisView.as_view(), name='participant_data_dated'),
    url(r'^(?P<username>\w+)/page/(?P<page>\d+)/$', 
        view=UserAnalysisView.as_view(), name='participant_data_paged'),
    url(r'^(?P<username>\w+)/$', 
        view=UserAnalysisView.as_view(), name='participant_data_named'),
    url(r'^$', 
        view=UserAnalysisView.as_view(), name='participant_data'),
    url(r'^interactions/(?P<username>\w+)/(?P<start>[\d\-]+)/(?P<end>[\d\-]+)/$', 
        view=cache_page(_CACH_TIMEOUT)(InteractionData.as_view()), 
        name='fb_interactions'),
    url(r'^detail/(?P<username>\w+)/(?P<data_type>\w+)/(?P<pk>\d+)/$', 
        view=cache_page(_CACH_TIMEOUT)(DetailData.as_view()), 
        name='fb_detail'),
)
