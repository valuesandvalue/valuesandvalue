# feeds.tasks

# PYTHON 
from datetime import timedelta

# DJANGO
from django.conf import settings
from django.core.mail import send_mail
from django.utils.timezone import now

# CELERY
from celery import task

# ACCOUNTS
from accounts.handlers import get_emails_for_feeds

# UTILS
from utils.slices import get_index_slice

# FEEDS
from .handlers import update_feed
from .models import (
    ExternalFeed,
    FeedEntry
)

_SLICE = 10
    
@task(ignore_result=True, name='feeds.tasks.aysnc_update_all_feeds')
def aysnc_update_all_feeds():
    index_slice = get_index_slice('update_all_feeds')
    index = index_slice.index
    limit = ExternalFeed.objects.filter(active=True).count()
    feeds = ExternalFeed.objects.filter(active=True)[index:index+_SLICE]
    for feed in feeds:
        newfeeds = update_feed(feed)
    index_slice.update_index(_SLICE, limit=limit)
    index_slice.save()

@task(ignore_result=True, name='feeds.tasks.aysnc_email_feeds')
def aysnc_email_feeds():
    timenow = now()
    pubtime = timenow - timedelta(days=1)
    newentries = FeedEntry.objects.filter(
                        published__gte=pubtime).order_by('-published')
    updated = {}
    for entry in newentries:
        feed = entry.feed
        if not updated.has_key(feed):
            updated[feed] = []
        updated[feed].append(entry)
    if updated:
        emails = get_emails_for_feeds()
        summaries = []
        listing = '\t%s\n\t%s\n\n'
        feeds = updated.keys()
        feeds.sort(key=lambda f: f.name)
        for feed in feeds:
            articles = updated[feed]
            if articles:
                titles = '\n'.join(
                                [listing % (a.title, a.link) for a in articles])
                summaries.append('%s:\n%s\n' % (feed.name, titles))
        message = 'updated feeds, date: %s\n\n%s' % (
                                timenow, '\n'.join(summaries))
        send_mail('Values & Value: news feed summary', 
                        message, 
                        settings.VAVS_EMAIL_FROM,
                        emails, 
                        fail_silently=False)
