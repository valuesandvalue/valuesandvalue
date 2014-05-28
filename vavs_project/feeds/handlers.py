# feeds.handlers

# PYTHON
import datetime
from HTMLParser import HTMLParser

# DJANGO
from django.utils.timezone import now, make_aware, get_default_timezone

# FEEDPARSER
import feedparser

# FEEDS
from .models import ExternalFeed, FeedEntry

class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
        
    def handle_data(self, d):
        self.fed.append(d)
        
    def get_data(self):
        return ''.join(self.fed)

def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()
    
def _convert_feed_date(feed_date):
    if feed_date:
        return make_aware(datetime.datetime(*feed_date[:6]), 
                get_default_timezone())
    else:
        return now()
    
def _print_entry(e):
    print e.title
    print e.published
    print e.link
    print e.summary
    print e.feed

def update_feed(extfeed, force=False):
    """Updates feed from external source."""
    last_updated = extfeed.updated
    newfeeds = []
    if extfeed.url:
        parsed = feedparser.parse(extfeed.url)
        for e in parsed.entries:
            if not FeedEntry.objects.filter(
                        feed=extfeed, title=e.title, link=e.link).exists():
                try:
                    published = _convert_feed_date(e.published_parsed)
                except:
                    published = now()
                if (last_updated and last_updated < published) or force:
                    entry = FeedEntry.objects.create(
                        feed=extfeed,
                        title=e.title,
                        published=published,
                        link=e.link,
                        summary=strip_tags(e.summary))
                    newfeeds.append(entry)
        if 'published_parsed' in parsed.feed:
            try:
                extfeed.updated = _convert_feed_date(
                                parsed.feed.published_parsed)
            except:
                extfeed.updated = now()
        elif 'updated_parsed' in parsed.feed:
            try:
                extfeed.updated = _convert_feed_date(parsed.feed.updated_parsed)
            except:
                extfeed.updated = now()
        else:
            extfeed.updated = now()
        extfeed.save()
    return newfeeds

def update_all_feeds():
    """Updates all active external feeds."""
    feeds = ExternalFeed.objects.filter(active=True)
    for feed in feeds:
        update_feed(feed)
