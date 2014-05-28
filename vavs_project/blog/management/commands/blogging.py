# blog.management.commands.blogging

# DJANGO
from django.conf import settings
from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand, CommandError

# BLOG
from blog.models import BlogCategory, Theme

class Command(BaseCommand):
    help = 'Commands for managing blog.'
    
    def handle(self, *args, **options):
        if len(args) > 0:
            cmd = args[0]
            if cmd == "setup":
                self.setup_blog()
            elif cmd == "site":
                site_domain = args[1]
                if len(args) > 2:
                    site_name = args[2]
                else:
                    site_name = None
                self.set_site(site_domain, site_name)
        else:
            print self.help
            
    def set_site(self, site_domain, site_name):
        site = Site.objects.get_current()
        site.domain = site_domain
        if site_name:
            site.name = site_name
        site.save()
        
    def setup_blog(self):
        # create basic categories
        BlogCategory.objects.all().delete()
        try:
            BlogCategory.objects.create(name='Articles', slug='articles')
        except:
            pass
        try:
            BlogCategory.objects.create(name='News', slug='news')
        except:
            pass
        try:
            BlogCategory.objects.create(name='Events', slug='events')
        except:
            pass
