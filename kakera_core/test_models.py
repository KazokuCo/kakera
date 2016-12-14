from django.test import TestCase
from django.core.exceptions import ValidationError
from kakera_core.models import validate_no_at_prefix, User

def TestValidateNoAtPrefix(TestCase):
    def test_no_at_prefix(self):
        validate_no_at_prefix('dril')

    def test_at_prefix(self):
        self.assertRaises(ValidationError, validate_no_at_prefix, '@dril')

class TestUser(TestCase):
    def test_twitter_field_accepts_no_at_prefix(self):
        user = User.objects.create_user(username='username', email='test@example.com')
        user.twitter = 'dril'
        user.full_clean()

    def test_twitter_field_rejects_at_prefix(self):
        user = User.objects.create_user(username='username', email='test@example.com')
        user.twitter = '@dril'
        self.assertRaises(ValidationError, user.full_clean)
