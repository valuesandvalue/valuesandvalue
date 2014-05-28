# addata.views

# DJANGO
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import get_object_or_404
from django.views.generic.base import TemplateView, View
from django.views.generic import (
    ArchiveIndexView,
    CreateView, 
    UpdateView, 
    DetailView
)

# DJANGO-BRACES
from braces.views import LoginRequiredMixin, StaffuserRequiredMixin

# ACCOUNTS
from accounts.handlers import get_staff_profile

# FBDATA
from fbdata.participant import get_participant_profile
from fbdata.utils import (
    can_access_user,
    isodatestr_to_datetime,
    timestamp_to_datetime
)

# ADDATA
from addata.activity import activity_data_json
from .api import (
    get_api_key,
    reset_api_key
)
from .details import (
    ad_details_for_hour_json,
    get_ad_data_json
)
from .handlers import get_user_data, get_all_user_data

class ApiKeyView(LoginRequiredMixin, TemplateView):
    template_name = 'addata/user_setup.html'
    
    def get(self, request, reset=False):
        user = request.user
        if user.is_staff:
            profile = get_staff_profile(user)
        else:
            profile = user.get_profile()
        if reset:
            api_key = reset_api_key(user)
        else:
            api_key = get_api_key(user)
        if api_key is None:
            return HttpResponseRedirect(reverse('participant_consent')) 
        else:
            return self.render_to_response({
                            'user':user, 
                            'profile':profile,
                            'api_key':api_key })

class AdData(LoginRequiredMixin, View):
    """Returns JSON ad data."""
    def get(self, request, username, start, end):
        if request.is_ajax()
            if not can_access_user(request.user, username):
                raise Http404
            else:
                user = get_object_or_404(User, username=username)
                participant = get_participant_profile(user)
                anon = False if request.user == user else participant.anon_data
                start = isodatestr_to_datetime(start)
                end = isodatestr_to_datetime(end)
                json_data = activity_data_json(
                         user, start, end, fbuser=participant.fbuser, anon=anon)
                return HttpResponse(json_data, content_type="application/json")
        else:
            raise Http404
            
class AdDetailData(LoginRequiredMixin, View):
    """Returns JSON detail data."""
    def get(self, request, username, ad_type, pk):
        if request.is_ajax()
            if not can_access_user(request.user, username):
                raise Http404
            else:
                user = get_object_or_404(User, username=username)
                participant = get_participant_profile(user)
                anon = False if request.user == user else participant.anon_data
                json_data = get_ad_data_json(ad_type, pk, anon=anon)
                return HttpResponse(json_data, content_type="application/json")
        else:
            raise Http404 
            
class AdActivityDetailData(LoginRequiredMixin, View):
    """Returns JSON detail data."""
    def get(self, request, username, hour):
        if request.is_ajax()
            if not can_access_user(request.user, username):
                raise Http404
            else:
                user = get_object_or_404(User, username=username)
                participant = get_participant_profile(user)
                hour = timestamp_to_datetime(hour)
                anon = False if request.user == user else participant.anon_data
                json_data = ad_details_for_hour_json(user, hour, anon=anon)
                return HttpResponse(json_data, content_type="application/json")
        else:
            raise Http404    
