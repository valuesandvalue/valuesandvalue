# gallery.views

# DJANGO
from django.contrib import messages
from django.views.generic import (
    CreateView, 
    UpdateView, 
    DetailView, 
    ListView
)

# DJANGO-BRACES
from braces.views import LoginRequiredMixin, StaffuserRequiredMixin

# GALLERY
from .forms import ImageFileForm
from .models import ImageFile

############
# IMAGE FILE
############
class ImageFileActionMixin(object):
    @property
    def action(self):
        msg = "{0} is missing action.".format(self.__class__)
        raise NotImplementedError(msg)
        
    def form_valid(self, form):
        msg = 'Image {0}.'.format(self.action)
        messages.info(self.request, msg)
        return super(ImageFileActionMixin, self).form_valid(form)
        
class ImageFileCreateView(
        StaffuserRequiredMixin, ImageFileActionMixin, CreateView):
    """View for creating a single image."""
    template_name = 'gallery/image_edit.html'
    model = ImageFile
    action = 'created'
    form_class = ImageFileForm
    
class ImageFileUpdateView(
        StaffuserRequiredMixin, ImageFileActionMixin, UpdateView):
    """View for editing a single image."""
    template_name = 'gallery/image_edit.html'
    model = ImageFile
    action = 'updated'
    form_class = ImageFileForm
    
class ImageFileDetailView(StaffuserRequiredMixin, DetailView):
    """View for displaying a single image."""
    template_name = 'gallery/image.html'
    model = ImageFile
    
class ImageFileListView(StaffuserRequiredMixin, ListView):
    """View for displaying list of images."""
    model = ImageFile
    paginate_by=10
    template_name = 'gallery/index.html'
