# addata.urls

# DJANGO
from django.conf.urls import patterns, include, url
from django.views.decorators.cache import cache_page

# ADDATA
from .views import (
    AdActivityDetailData,
    AdData,
    AdDetailData,
    ApiKeyView
)

_CACH_TIMEOUT = 60 * 60
            
urlpatterns = patterns('',
    url(r'^detail/(?P<username>\w+)/(?P<ad_type>\w+)/(?P<pk>\d+)/$', 
            view=cache_page(_CACH_TIMEOUT)(AdDetailData.as_view()), 
            name='ad_detail'),
    url(r'^hour/(?P<username>\w+)/(?P<hour>[\d\-]+)/$', 
            view=cache_page(_CACH_TIMEOUT)(AdActivityDetailData.as_view()), 
            name='ad_hour'),
    url(r'^reset/$', view=ApiKeyView.as_view(), 
            kwargs={'reset':True}, name='reset_apikey'),
    url(r'^$', view=ApiKeyView.as_view(), name='setup_apikey'),
)
