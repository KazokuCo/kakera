from django.core.cache import cache
from django.core.management.base import BaseCommand
from wagtail.wagtailcore.models import Site
from kakera_core.ext.cloudflare import purge_site

class Command(BaseCommand):
    help = "Purges all caches, backend and frontend"

    def handle(self, *args, **options):
        cache.clear()
        for site in Site.objects.all():
            purge_site(site)
