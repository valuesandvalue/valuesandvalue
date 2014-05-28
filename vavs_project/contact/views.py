# contact.views

# DJANGO
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.mail import BadHeaderError
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, Http404 
from django.views.generic import (
    ListView,
    CreateView, 
    UpdateView, 
    DetailView,
    FormView,
    TemplateView
)

# DJANGO-BRACES
from braces.views import LoginRequiredMixin, StaffuserRequiredMixin

# COMMENTS
from .forms import ContactForm, ParticipateForm
from .models import Participate

############
# CONTACT
############
class ContactView(FormView):
    template_name = 'contact/contact_form.html'
    form_class = ContactForm
    success_url = '/contact/thankyou/'

    def form_valid(self, form):
        try:
            form.send_email()
        except BadHeaderError:
            return super(ContactView, self).form_invalid(form)
        return super(ContactView, self).form_valid(form)

############
# INTEREST
############
participant_list_view = ListView.as_view(
            queryset=Participate.objects.all(),
            paginate_by=10, 
            allow_empty=True,
            template_name='contact/participate_index.html')

@login_required
@user_passes_test(lambda u:u.is_staff, login_url='/login/')
def delete_participant_view(request, pk):
    try:
        Participate.objects.get(pk=pk).delete()
    except Participate.DoesNotExist:
        raise Http404
    return HttpResponseRedirect(reverse('participant_index'))
    
class ParticipateActionMixin(object):
    @property
    def action(self):
        msg = "{0} is missing action.".format(self.__class__)
        raise NotImplementedError(msg)
        
    def form_valid(self, form):
        msg = 'Participate {0}.'.format(self.action)
        messages.info(self.request, msg)
        return super(ParticipateActionMixin, self).form_valid(form)
        
class ParticipateCreateView(CreateView):
    """View for registering to participate."""
    template_name = 'contact/participate.html'
    model = Participate
    action = 'created'
    form_class = ParticipateForm
    
    def form_valid(self, form):
        try:
            form.send_email()
        except BadHeaderError:
            return super(ParticipateCreateView, self).form_invalid(form)
        return super(ParticipateCreateView, self).form_valid(form)
    
class ParticipateUpdateView( 
            StaffuserRequiredMixin,
            UpdateView):
    """View for editing participate details."""
    template_name = 'contact/participate_edit.html'
    model = Participate
    action = 'updated'
    form_class = ParticipateForm
    
class ParticipateDetailView(DetailView):
    """View for displaying participate details."""
    template_name = 'contact/participate.html'
    model = Participate
    
