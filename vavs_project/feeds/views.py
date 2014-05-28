# feeds.views

# DJANGO
from django.contrib import messages
from django.views.generic.base import TemplateView
from django.views.generic import CreateView, UpdateView, DetailView

# DJANGO-BRACES
from braces.views import LoginRequiredMixin, StaffuserRequiredMixin

# FEEDS
from .forms import ExternalFeedForm, PageLinkForm
from .models import ExternalFeed, PageLink

############
# EXTERNAL FEED
############
class ExternalFeedActionMixin(object):
    @property
    def action(self):
        msg = "{0} is missing action.".format(self.__class__)
        raise NotImplementedError(msg)
        
    def form_valid(self, form):
        msg = 'Feed {0}.'.format(self.action)
        messages.info(self.request, msg)
        return super(ExternalFeedActionMixin, self).form_valid(form)
        
class ExternalFeedCreateView(
        StaffuserRequiredMixin, ExternalFeedActionMixin, CreateView):
    """View for creating a single feed."""
    template_name = 'feeds/feed_edit.html'
    model = ExternalFeed
    action = 'created'
    form_class = ExternalFeedForm
    
class ExternalFeedUpdateView(
        StaffuserRequiredMixin, ExternalFeedActionMixin, UpdateView):
    """View for editing a single feed."""
    template_name = 'feeds/feed_edit.html'
    model = ExternalFeed
    action = 'updated'
    form_class = ExternalFeedForm
    
class ExternalFeedDetailView(DetailView):
    """View for displaying a single feed."""
    template_name = 'feeds/feed.html'
    model = ExternalFeed
    
############
# PAGE LINK
############
class PageLinkActionMixin(object):
    @property
    def action(self):
        msg = "{0} is missing action.".format(self.__class__)
        raise NotImplementedError(msg)
        
    def form_valid(self, form):
        msg = 'Page link {0}.'.format(self.action)
        messages.info(self.request, msg)
        return super(PageLinkActionMixin, self).form_valid(form)
        
class PageLinkCreateView(
        StaffuserRequiredMixin, PageLinkActionMixin, CreateView):
    """View for creating a single link."""
    template_name = 'links/link_edit.html'
    model = PageLink
    action = 'created'
    form_class = PageLinkForm
    
class PageLinkUpdateView(
        StaffuserRequiredMixin, PageLinkActionMixin, UpdateView):
    """View for editing a single link."""
    template_name = 'links/link_edit.html'
    model = PageLink
    action = 'updated'
    form_class = PageLinkForm
