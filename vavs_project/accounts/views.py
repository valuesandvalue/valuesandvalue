# accounts.views

# DJANGO
from django.conf import settings
from django.contrib import auth
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect 
from django.views.generic import (
    FormView,
    TemplateView
)

# DJANGO-BRACES
from braces.views import LoginRequiredMixin

# FBDATA
from fbdata.participant import (
    get_participants,
    get_participant_profile
)

# SURVEYS
from surveys.handlers import get_answers_for_email
from surveys.models import (
    Respondent,
    Survey
)

# ACCOUNTS
from .forms import (
    ConsentForm,
    LoginForm,
    StaffProfileForm
)
from .handlers import get_staff_profile

############
# CONTACT
############
class LoginView(FormView):
    template_name = 'accounts/login.html'
    form_class = LoginForm
    success_url = '/accounts/profile/'
    redirect_url = '/accounts/denied/'
    
    def get_redirect_url(self):
        return self.redirect_url

    def form_valid(self, form):
        if form.login(self.request):
            return super(LoginView, self).form_valid(form)
        else:
            return HttpResponseRedirect(self.get_redirect_url())
        
class LogoutView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/logout.html'
    
    def get(self, request):
        auth.logout(request)
        return super(LogoutView, self).get(request)
        
class ConsentView(FormView):
    template_name = 'accounts/consent.html'
    form_class = ConsentForm
    success_url = '/accounts/profile/'
    redirect_url = '/accounts/denied/'
    
    def get_redirect_url(self):
        return self.redirect_url

    def form_valid(self, form):
        if form.login(self.request):
            return super(LoginView, self).form_valid(form)
        else:
            return HttpResponseRedirect(self.get_redirect_url())
            
class ConsentView(TemplateView):
    template_name = 'accounts/consent.html'
    
    def get(self, request):
        if request.user.is_staff:
            return HttpResponseRedirect(reverse('profile'))
        participant = get_participant_profile(request.user)
        if participant.consent:
            return HttpResponseRedirect(reverse('profile'))
        else:
            form = ConsentForm()
            return self.render_to_response({'form':form})
        
    def post(self, request):
        if request.user.is_staff:
            return HttpResponseRedirect(reverse('profile'))
        form = ConsentForm(request.POST)
        if form.is_valid():
            participant = get_participant_profile(request.user)
            participant.consent = True
            participant.save()
            return HttpResponseRedirect(reverse('profile'))
        else:
            return self.render_to_response({'form':form, 'survey':survey})
    
class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/profile.html'
    
    def _user_surveys(self, user):
        survey_data = {}
        surveys = Survey.objects.filter(
                    questions__answers__respondent__email=user.email
                ).order_by('created')
        for survey in surveys:
            survey_data[survey] = Respondent.objects.filter(
                                    email=user.email,
                                    survey_answers__question__survey=survey)[0]
        return survey_data
    
    def _staff_data(self, user, profile, form):
        data = {'user':user}
        data['profile'] = profile
        data['form'] = form
        data['surveys'] = Survey.objects.all().order_by('created')
        data['participants'] = get_participants()
        return data
    
    def get(self, request):
        user = request.user
        if user.is_staff:
            profile = get_staff_profile(user)
            form = StaffProfileForm(instance=profile)
            data = self._staff_data(user, profile, form)
        else:
            try:
                profile = user.get_profile()
            except:
                profile = None
            participant = get_participant_profile(user)
            if participant.consent:
                data = {'user':user, 
                    'profile':profile, 
                    'participant':participant,
                    'surveys':self._user_surveys(user)}
            else:
                return HttpResponseRedirect(reverse('participant_consent'))
        return self.render_to_response(data)
        
    def post(self, request):
        user = request.user
        if user.is_staff:
            profile = get_staff_profile(user)
            form = StaffProfileForm(request.POST, instance=profile)
            if form.is_valid():
                form.save()
                return HttpResponseRedirect(reverse('profile'))
            else:
                data = self._staff_data(user, profile, form)
        else:
            data = {'user':user} 
        return self.render_to_response(data)

