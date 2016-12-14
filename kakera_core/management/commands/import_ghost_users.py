import argparse
import json
from django.core.management.base import BaseCommand
from django.db import transaction
from kakera_core.models import User

class Command(BaseCommand):
    help = "Imports users from a Ghost database dump"

    def add_arguments(self, parser):
        parser.add_argument('file', type=argparse.FileType('r', encoding='utf-8'), help='JSON file to load.')

    def handle(self, *args, **options):
        data = json.load(options['file'])

        with transaction.atomic():
            for userdata in data['db'][0]['data']['users']:
                # self.stdout.write(json.dumps(userdata))

                username = userdata['name']
                first_name = ""
                last_name = ""
                if ' ' in username:
                    first_name, last_name = username.split(' ', 1)
                    username = userdata['slug']

                email = userdata['email'] or ""
                twitter = userdata['twitter'] or ""
                bio = userdata['bio'] or ""

                if twitter.startswith('@'):
                    twitter = twitter[1:]

                try:
                    user = User.objects.get(username=username)
                    self.stdout.write("  {0}".format(username))
                except User.DoesNotExist:
                    user = User.objects.create_user(username=username)
                    self.stdout.write("+ {0}".format(username))

                user.first_name = first_name
                user.last_name = last_name
                user.email = email
                user.bio = bio
                user.twitter = twitter
                user.full_clean()
                user.save()
