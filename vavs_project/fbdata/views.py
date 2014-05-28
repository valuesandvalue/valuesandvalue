# fbdata.views

# DJANGO
from django.contrib import messages
from django.contrib.auth.models import User
#from django.db.models import Max
#from django.db.models import Q
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

# FBDATA
from .details import get_fbobject_data_json
from .fbids import get_fbuser_from_djuser
from .graphs import narrative_data_json
from .models import UserAnalysis
from .participant import get_participant_profile
from .utils import (
    can_access_user,
    isodatestr_to_date,
    isodatestr_to_datetime,
    recent_time_frame
)
  
def _json_error(message):
    return '{"type":"error", "message":%s}' % message
      
class UserAnalysisView(LoginRequiredMixin, TemplateView):
    """View for single user data."""
    template_name = 'fbdata/user_analysis.html'
    
    def get(self, request, username=None, start=None, end=None, page=None):
        username = username or request.user.username
        if not can_access_user(request.user, username):
            raise Http404
        else:
            user = get_object_or_404(User, username=username)
            participant = get_participant_profile(user)  
            fbuser = participant.fbuser
            if start and end:
                start = isodatestr_to_date(start)
                end = isodatestr_to_date(end)
                pager = None
            elif page:
                page = int(page)
                start, end = participant.page_dates(page)
                start = start.date()
                end = end.date()
                pager = participant.paginate(page=page)
            else:
                start, end = participant.recent_time_frame()
                if start and end:
                    start = start.date()
                    end = end.date()
                    pager = participant.paginate()
                else:
                    pager = None
            return self.render_to_response({
                        'user': user,
                        'username': username,
                        'fbuser': fbuser, 
                        'participant': participant,
                        'start': start,
                        'end': end,
                        'pager': pager})
 
class InteractionData(LoginRequiredMixin, View):
    """Returns JSON interaction data."""
    def get(self, request, username, start, end):
        #if request.is_ajax()
        if not can_access_user(request.user, username):
            raise Http404
        else:
            user = get_object_or_404(User, username=username)
            participant = get_participant_profile(user)
            anon = False if request.user == user else participant.anon_data
            start = isodatestr_to_datetime(start)
            end = isodatestr_to_datetime(end)
            json_data = narrative_data_json(
                        user, start, end, fbuser=participant.fbuser, anon=anon)
            return HttpResponse(json_data, content_type="application/json")
            
class DetailData(LoginRequiredMixin, View):
    """Returns JSON detail data."""
    def get(self, request, username, data_type, pk):
        #if request.is_ajax()
        if not can_access_user(request.user, username):
            raise Http404
        else:
            user = get_object_or_404(User, username=username)
            participant = get_participant_profile(user)
            anon = False if request.user == user else participant.anon_data
            json_data = get_fbobject_data_json(data_type, pk, anon=anon)
            return HttpResponse(json_data, content_type="application/json")
