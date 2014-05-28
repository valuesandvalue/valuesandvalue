# publications.views

# DJANGO
from django.contrib import messages
from django.views.generic import CreateView, UpdateView, DetailView

# DJANGO-BRACES
from braces.views import LoginRequiredMixin, StaffuserRequiredMixin

# GALLERY
from .forms import PublicationForm
from .models import Publication

############
# IMAGE FILE
############
class PublicationActionMixin(object):
    @property
    def action(self):
        msg = "{0} is missing action.".format(self.__class__)
        raise NotImplementedError(msg)
        
    def form_valid(self, form):
        msg = 'Publication {0}.'.format(self.action)
        messages.info(self.request, msg)
        return super(PublicationActionMixin, self).form_valid(form)
        
class PublicationCreateView(
        StaffuserRequiredMixin, PublicationActionMixin, CreateView):
    """View for creating a single publication."""
    template_name = 'publications/publication_edit.html'
    model = Publication
    action = 'created'
    form_class = PublicationForm
    
class PublicationUpdateView(
        StaffuserRequiredMixin, PublicationActionMixin, UpdateView):
    """View for editing a single publication."""
    template_name = 'publications/publication_edit.html'
    model = Publication
    action = 'updated'
    form_class = PublicationForm
    
class PublicationDetailView(DetailView):
    """View for displaying a single publication."""
    template_name = 'publications/publication.html'
    model = Publication
