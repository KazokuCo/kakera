from django.core.management.base import BaseCommand
from django.db import transaction
from kakera_blog.models import BlogPage, StaticPage

ADMIN_FILTERS = [
    'max-165x165',
    'max-800x600',
]

COVER_FILTERS = [
    'original',
    'height-562',
    'max-500x300',
] + ADMIN_FILTERS

BLOCK_FILTERS = [
    'original',
    'height-562',
] + ADMIN_FILTERS

class Command(BaseCommand):
    help = "Rebuilds precompiled post HTML"

    def add_arguments(self, parser):
        parser.add_argument('--quick', action='store_true')

    def handle(self, *args, **options):
        for page in list(BlogPage.objects.all()) + list(StaticPage.objects.all()):
            print("## {}".format(page.title))
            with transaction.atomic():
                if not options['quick']:
                    if page.cover_image:
                        print("-> rendering cover...")
                        for ft in COVER_FILTERS:
                            print("   -> {0}".format(ft))
                            page.cover_image.get_rendition(ft)
                    for block in page.body:
                        if block.block_type == 'image':
                            print("-> rendering: {}".format(block.value))
                            for ft in BLOCK_FILTERS:
                                print("    -> {0}".format(ft))
                                block.value.get_rendition(ft)
                print("-> cooking...")
                page.save()
