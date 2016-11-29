from django.db import models

from wagtail.wagtailcore import blocks
from wagtail.wagtailcore.models import Page
from wagtail.wagtailcore.fields import StreamField
from wagtail.wagtailsearch import index
from wagtail.wagtailadmin.edit_handlers import MultiFieldPanel, FieldPanel, StreamFieldPanel
from wagtail.wagtailimages.blocks import ImageChooserBlock
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel
from wagtail.wagtailembeds.blocks import EmbedBlock

class MarkdownBlock(blocks.TextBlock):
    class Meta:
        template = 'kakera_blog/blocks/markdown.html'

class DefaultStreamBlock(blocks.StreamBlock):
    markdown = MarkdownBlock()
    image = ImageChooserBlock()
    embed = EmbedBlock()

class BlogPage(Page):
    published = models.DateTimeField()

    cover_image = models.ForeignKey('wagtailimages.Image', null=True, blank=True, on_delete=models.SET_NULL, related_name='+')
    cover_embed = models.CharField(max_length=1000, null=True, blank=True)

    body = StreamField(DefaultStreamBlock())

    search_fields = Page.search_fields + [
        index.SearchField('title'),
    ]

    content_panels = Page.content_panels + [
        FieldPanel('published'),
        MultiFieldPanel([
            ImageChooserPanel('cover_image'),
            FieldPanel('cover_embed'),
        ], "Cover"),
        StreamFieldPanel('body'),
    ]

    # Only allow blog posts under index pages, disallow subpages
    parent_page_types = ['kakera_blog.BlogIndexPage']
    subpage_types = []

class BlogIndexPage(Page):
    def get_context(self, request):
        context = super(BlogIndexPage, self).get_context(request)
        context['blog_entries'] = BlogPage.objects.child_of(self).live()
        return context

class StaticPage(Page):
    cover_image = models.ForeignKey('wagtailimages.Image', null=True, blank=True, on_delete=models.SET_NULL, related_name='+')

    body = StreamField(DefaultStreamBlock())

    search_fields = Page.search_fields + [
        index.SearchField('title'),
    ]

    content_panels = Page.content_panels + [
        ImageChooserPanel('cover_image'),
        StreamFieldPanel('body'),
    ]
