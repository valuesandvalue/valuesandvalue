# comments.views

# PYTHON
import json

# DJANGO
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.urlresolvers import reverse
from django.db.models import Max
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404
from django.views.generic.base import TemplateView
from django.views.generic import (
    ArchiveIndexView,
    CreateView, 
    UpdateView, 
    DetailView
)

# CAPTCHA
from captcha.models import CaptchaStore
from captcha.helpers import captcha_image_url

# DJANGO-BRACES
from braces.views import LoginRequiredMixin, StaffuserRequiredMixin

# COMMENTS
from .forms import CommentForm
from .models import Comment

############
# COMMENTS ARCHIVE
############
class CommentArchiveView(ArchiveIndexView):
    extra_context = None
    
    def get_context_data(self, **kwargs):
        context = super(CommentArchiveView, self).get_context_data(**kwargs)
        if self.extra_context:
            context.update(self.extra_context)
        return context
    
def comment_archive_view(request, **kwargs):
    form = CommentForm()
    return CommentArchiveView.as_view(
            queryset=Comment.objects.filter(display=True),
            paginate_by=10, 
            allow_empty=True,
            date_field="created",
            template_name='comments/index.html',
            extra_context={'form':form})(request, **kwargs)

@login_required
@user_passes_test(lambda u:u.is_staff, login_url='/login/')
def delete_comment_view(request, pk):
    try:
        Comment.objects.get(pk=pk).delete()
    except Comment.DoesNotExist:
        raise Http404
    return HttpResponseRedirect(reverse('current_comments'))
     
############
# COMMENTS
############
class CommentActionMixin(object):
    @property
    def action(self):
        msg = "{0} is missing action.".format(self.__class__)
        raise NotImplementedError(msg)
        
    def form_valid(self, form):
        msg = 'Comment {0}.'.format(self.action)
        messages.info(self.request, msg)
        return super(CommentActionMixin, self).form_valid(form)
        
class CommentCreateView(CreateView):
    """View for creating a single comment."""
    template_name = 'comments/comment_edit.html'
    model = Comment
    action = 'created'
    form_class = CommentForm
    
    def form_invalid(self, form):
        if self.request.is_ajax():
            json_pkt = dict()
            json_pkt['status'] = 0
            json_pkt['form_errors'] = form.errors
            json_pkt['new_cptch_key'] = CaptchaStore.generate_key()
            json_pkt['new_cptch_image'] = captcha_image_url(
                                            json_pkt['new_cptch_key'])
            return HttpResponse(
                    json.dumps(json_pkt), content_type='application/json')
        else:
            return super(CommentCreateView, self).form_invalid(form) 

    def form_valid(self, form):
        form.save()
        if self.request.is_ajax():
            json_pkt = dict()
            json_pkt['status'] = 1
            json_pkt['new_cptch_key'] = CaptchaStore.generate_key()
            json_pkt['new_cptch_image'] = captcha_image_url(
                                            json_pkt['new_cptch_key'])
            return HttpResponse(
                    json.dumps(json_pkt), content_type='application/json')
        else:
            return super(CommentCreateView, self).form_valid(form) 
    
class CommentUpdateView(UpdateView):
    """View for editing a single comment."""
    template_name = 'comments/comment_edit.html'
    model = Comment
    action = 'updated'
    form_class = CommentForm
    
class CommentDetailView(DetailView):
    """View for displaying a single comment."""
    template_name = 'comments/comment.html'
    model = Comment
