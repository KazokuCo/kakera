import argparse
import json
from django.core.management.base import BaseCommand
from django.db import transaction
from taggit.models import Tag

class Command(BaseCommand):
    help = "Imports tags from a Ghost database dump"

    def add_arguments(self, parser):
        parser.add_argument('file', type=argparse.FileType('r', encoding='utf-8'), help="JSON file to load.")

    def handle(self, *args, **options):
        data = json.load(options['file'])

        with transaction.atomic():
            for tagdata in data['db'][0]['data']['tags']:
                slug = tagdata['slug']
                name = tagdata['name']
                tag, created = Tag.objects.update_or_create(slug=slug, defaults={'name': name})
                print("{0} {1}".format("+" if created else " ", tag.name))
