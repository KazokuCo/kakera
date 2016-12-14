import io
import json
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.core.management import call_command
from kakera_core.models import User

class TestImportGhostUsers(TestCase):
    def gen_db(self, *users):
        return {
            "db": [{
                "data": {
                    "users": users,
                }
            }]
        }

    def gen_user(self, **kwargs):
        return {**{
            "id": 2,
            "uuid": "40d0f4d2-804f-484c-baa9-4e3f35d9f1b7",
            "name": "username",
            "slug": "username",
            "password": "",
            "email": "test@example.com",
            "image": "http://placekitten.com/g/500/500",
            "cover": "http://placekitten.com/g/1000/300",
            "bio": "Lorem ipsum dolor sit amet.",
            "website": "http://google.com/",
            "location": None,
            "facebook": None,
            "twitter": None,
            "accessibility": None,
            "status": "active",
            "language": "en_US",
            "visibility": "public",
            "meta_title": None,
            "meta_description": None,
            "tour": None,
            "last_login": "2016-10-29T08:12:34.000Z",
            "created_at": "2016-10-29T08:12:34.000Z",
            "created_by": 1,
            "updated_at": "2016-10-29T08:12:34.000Z",
            "updated_by": 2,
        }, **kwargs}

    def test_import_single_user(self):
        u = self.gen_user()

        stdout = io.StringIO()
        call_command('import_ghost_users', '-', file=io.StringIO(json.dumps(self.gen_db(u))), stdout=stdout)
        self.assertIn("+ username", stdout.getvalue())

        user = User.objects.get(username='username')
        self.assertEqual("username", user.username)
        self.assertEqual("test@example.com", user.email)
        self.assertEqual("Lorem ipsum dolor sit amet.", user.bio)

    def test_update_single_user(self):
        User.objects.create_user(username='username', email='wrong@example.com', bio='wrong')

        u = self.gen_user()

        stdout = io.StringIO()
        call_command('import_ghost_users', '-', file=io.StringIO(json.dumps(self.gen_db(u))), stdout=stdout)
        self.assertIn("  username", stdout.getvalue())

        user = User.objects.get(username='username')
        self.assertEqual("username", user.username)
        self.assertEqual("test@example.com", user.email)
        self.assertEqual("Lorem ipsum dolor sit amet.", user.bio)

    def test_import_space_in_username(self):
        u = self.gen_user(name='User Name', slug='user_name')
        call_command('import_ghost_users', '-', file=io.StringIO(json.dumps(self.gen_db(u))), stdout=io.StringIO())
        user = User.objects.get(username='user_name')
        self.assertEqual("User", user.first_name)
        self.assertEqual("Name", user.last_name)

    def test_import_twitter_invalid(self):
        u = self.gen_user(twitter='@dril')
        call_command('import_ghost_users', '-', file=io.StringIO(json.dumps(self.gen_db(u))), stdout=io.StringIO())
        user = User.objects.get(username='username')
        self.assertEqual('dril', user.twitter)

    def test_import_twitter(self):
        u = self.gen_user(twitter='dril')
        call_command('import_ghost_users', '-', file=io.StringIO(json.dumps(self.gen_db(u))), stdout=io.StringIO())
        user = User.objects.get(username='username')
        self.assertEqual('dril', user.twitter)
