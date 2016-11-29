from wagtail.tests.utils import WagtailPageTests
from kakera_blog.models import BlogPage, BlogIndexPage

class TestBlogPage(WagtailPageTests):
    def test_can_create_under_index(self):
        self.assertCanCreateAt(BlogIndexPage, BlogPage)

    def test_cant_create_under_self(self):
        self.assertCanNotCreateAt(BlogPage, BlogPage)
