# blog.templatetags.blog_tags

# DJANGO
from django import template
from django.template.defaultfilters import stringfilter
from django.template.loader import render_to_string
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe

# PREPARATION
register = template.Library()

########################
# FRONT FLOW FILTERS
########################
@register.filter(name='fancywords', needs_autoescape=True)
def fancywords(value, url=None, autoescape=None):
    length = 4
    words = value.split()
    if autoescape:
        esc = conditional_escape
    else:
        esc = lambda x: x
    parta = esc(' '.join(words[0:length]))
    partb = esc(' '.join(words[length:]))
    if url:
        html = '<span class="fancy-text"><a href="%s">%s</a></span> <span>%s</span>' % (
                esc(url),parta,partb)
    else:
        html = '<span class="fancy-text">%s</span> <span>%s</span>' % (
                parta,partb)
    return mark_safe(unicode(html))

########################
# FRONT FLOW TAGS
########################
@register.tag(name="front_flow")
@stringfilter
def do_front_flow(parser, token):
    try:
        tokens = token.split_contents()
        tag_name = tokens[0]
        blogs_var = tokens[1]
        comments_var = tokens[2]
        publications_var = tokens[3]
        feeds_var = tokens[4]
        colsize_var = tokens[5]
    except ValueError:
        raise template.TemplateSyntaxError(
                "%r tag requires four arguments" % token.contents.split()[0])
    return FrontFlowNode(blogs_var, comments_var, publications_var, feeds_var, colsize_var)
    
class FrontFlowNode(template.Node):
    div_classes = "vavs-front-col"
    def __init__(self, blogs_var, comments_var, publications_var, feeds_var, colsize_var):
        self.blogs_var = template.Variable(blogs_var)
        self.comments_var = template.Variable(comments_var)
        self.publications_var = template.Variable(publications_var)
        self.feeds_var = template.Variable(feeds_var)
        self.colsize_var = template.Variable(colsize_var)
        
    def render(self, context):
        from random import shuffle
        blogs = self.blogs_var.resolve(context)
        comments = self.comments_var.resolve(context)
        publications = self.publications_var.resolve(context)
        feeds = self.feeds_var.resolve(context)
        colsize = self.colsize_var.resolve(context)
        items_html = []
        for item in blogs:
            items_html.append(render_to_string(
                'widgets/front_blog_widget.html', 
                {'item':item, 'section_title':'Articles, News & Events'}))
        for item in comments:
            items_html.append(render_to_string(
                'widgets/front_comment_widget.html', 
                {'item':item, 'section_title':'Facebook Experiences'}))
        for item in publications:
            items_html.append(render_to_string(
                'widgets/front_publication_widget.html', 
                {'item':item, 'section_title':'Publications'}))
        for item in feeds:
            items_html.append(render_to_string(
                'widgets/front_feed_widget.html', 
                {'item':item, 'section_title':'Feeds & Links'}))
        # shuffle
        shuffle(items_html)
        # put into colums
        divstr = '<div class="%s">\n' % self.div_classes
        html = divstr
        for index, element in enumerate(items_html):
            if index > 0 and index % colsize == 0:
                html += '</div>\n'
                html += divstr
            html += element+'\n'
        html += '</div>\n'
        return html
