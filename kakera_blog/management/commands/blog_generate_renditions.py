from django.core.management.base import BaseCommand
from kakera_blog.models import BlogPage

ADMIN_FILTERS = [
    'max-165x165',
    'max-800x600',
]

COVER_FILTERS = [
    'original',
    'max-500x300',
] + ADMIN_FILTERS

BLOCK_FILTERS = [
    'original',
] + ADMIN_FILTERS

class Command(BaseCommand):
    help = "Batch generates image renditions for blog images"

    def handle(self, *args, **options):
        for page in BlogPage.objects.all():
            print("Processing: {}".format(page.title))
            if page.cover_image:
                print("-> Cover")
                for ft in COVER_FILTERS:
                    print("   -> {0}".format(ft))
                    page.cover_image.get_rendition(ft)
            for block in page.body:
                if block.block_type == 'image':
                    print("-> Block: {}".format(block.value))
                    for ft in BLOCK_FILTERS:
                        print("   -> {0}".format(ft))
                        block.value.get_rendition(ft)
