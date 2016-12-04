from django.test import TestCase
from kakera_core.templatetags.kakera_tags import force_https

class TestForceHTTPS(TestCase):
    def test_http_url(self):
        self.assertEqual(force_https("http://example.com/"), "https://example.com/")

    def test_https_url(self):
        self.assertEqual(force_https("https://example.com/"), "https://example.com/")

    def test_ftp_url(self):
        self.assertEqual(force_https("ftp://example.com/"), "ftp://example.com/")
