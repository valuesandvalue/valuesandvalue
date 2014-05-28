# blog.rssfeeds

# DJANGO
from django.contrib.syndication.views import Feed

# BLOG
from .models import BlogItem

class LatestBlogFeed(Feed):
    title = 'Values & Value'
    link = '/feed/'
    description = 'Articles and postings from the Values & Value project.'
    title_template = 'blog/feed_title.txt'
    description_template = 'blog/feed_description.txt'

    def items(self):
        return BlogItem.objects.order_by('-created')[:5]
