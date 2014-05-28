# accounts.urls

# DJANGO
from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView

# ACCOUNTS
from .views import (
    ConsentView,
    LoginView, 
    LogoutView, 
    ProfileView
)

urlpatterns = patterns('',
    url(r'^login/$', view=LoginView.as_view(), name='login'),
    url(r'^logout/$', view=LogoutView.as_view(), name='logout'),
    url(r'^profile/$', view=ProfileView.as_view(), name='profile'),
    url(r'^consent/$', view=ConsentView.as_view(), name='participant_consent'),
    url(r'^denied/$', view=TemplateView.as_view(
                        template_name='accounts/denied.html'), 
                        name='denied'),
)
