# blog.views

# DJANGO
from django.contrib import messages
from django.db.models import Max
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.views.generic.base import TemplateView
from django.views.generic import (
    ArchiveIndexView,
    CreateView, 
    UpdateView, 
    DetailView
)

# DJANGO-BRACES
from braces.views import LoginRequiredMixin, StaffuserRequiredMixin

# BLOG
from .forms import BlogItemForm, ThemeForm
from .models import BlogItem, BlogCategory, Theme

############
# BLOG CATEGORIES
############
class BlogCategoryArchiveView(ArchiveIndexView):
    extra_context = None
    
    def get_context_data(self, **kwargs):
        context = super(
                    BlogCategoryArchiveView, self).get_context_data(**kwargs)
        context.update(self.extra_context)
        return context
    
def blog_category_view(request, slug, **kwargs):
    category = get_object_or_404(BlogCategory, slug=slug)
    if category.name == 'Events':
        date_field = "display_date"
        allow_future = True
    else:
        date_field = "created"
        allow_future = False
    return BlogCategoryArchiveView.as_view(
            queryset=BlogItem.objects.filter(display=True, category=category),
            paginate_by=10, 
            allow_empty=True,
            allow_future=allow_future,
            date_field=date_field,
            template_name='blog/index.html',
            extra_context={'category':category, 
                        'page_kwargs':{'slug':category.name.lower()}
                    })(request, **kwargs)
    
############
# BLOG ITEMS
############
class BlogItemActionMixin(object):
    @property
    def action(self):
        msg = "{0} is missing action.".format(self.__class__)
        raise NotImplementedError(msg)
        
    def form_valid(self, form):
        msg = 'Blog item {0}.'.format(self.action)
        messages.info(self.request, msg)
        return super(BlogItemActionMixin, self).form_valid(form)
        
class BlogItemCreateView(
        StaffuserRequiredMixin, BlogItemActionMixin, CreateView):
    """View for creating a single blog item."""
    template_name = 'blog/item_edit.html'
    model = BlogItem
    action = 'created'
    form_class = BlogItemForm
    
class BlogItemUpdateView(
        StaffuserRequiredMixin, BlogItemActionMixin, UpdateView):
    """View for editing a single blog item."""
    template_name = 'blog/item_edit.html'
    model = BlogItem
    action = 'updated'
    form_class = BlogItemForm
    
class BlogItemDetailView(DetailView):
    """View for displaying a single blog item."""
    template_name = 'blog/item.html'
    model = BlogItem

############
# THEMES
############
class ThemeActionMixin(object):
    @property
    def action(self):
        msg = "{0} is missing action.".format(self.__class__)
        raise NotImplementedError(msg)
        
    def form_valid(self, form):
        msg = 'Theme {0}.'.format(self.action)
        messages.info(self.request, msg)
        return super(ThemeActionMixin, self).form_valid(form)
        
class ThemeCreateView(StaffuserRequiredMixin, ThemeActionMixin, CreateView):
    """View for creating a single theme."""
    template_name = 'themes/theme_edit.html'
    model = Theme
    action = 'created'
    form_class = ThemeForm
    
class ThemeUpdateView(StaffuserRequiredMixin, ThemeActionMixin, UpdateView):
    """View for editing a single theme."""
    template_name = 'themes/theme_edit.html'
    model = Theme
    action = 'updated'
    form_class = ThemeForm
    
class ThemeDetailView(DetailView):
    """View for displaying a single theme."""
    template_name = 'themes/theme.html'
    model = Theme

############
# FRONT PAGE
############ 
class FrontPageView(TemplateView):
    template_name = 'front.html'
    
    def _get_template_vars(self, request):
        from comments.models import Comment
        from feeds.models import FeedEntry
        from publications.models import Publication
        blogs = BlogItem.objects.filter(display=True).order_by('-created')[:4]
        items = blogs.count()
        comments = Comment.objects.all().order_by('-created')[:4]
        items += comments.count()
        publications = Publication.objects.all().order_by('-published')[:4]
        items += publications.count()
        feeds = FeedEntry.objects.filter(~Q(summary='')).order_by('-published')[:24-items]
        return {'comments':comments, 'blogs':blogs, 'publications':publications, 'feeds':feeds}
        
    def get(self, request):
        return self.render_to_response(self._get_template_vars(request))
