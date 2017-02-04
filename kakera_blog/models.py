from django.dispatch import receiver
from django.db import models
from django.db.models.signals import pre_delete
from django.conf import settings
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import redirect

from wagtail.wagtailcore import blocks
from wagtail.wagtailcore.models import Page
from wagtail.wagtailcore.fields import StreamField
from wagtail.wagtailcore.signals import page_published
from wagtail.wagtailsearch import index
from wagtail.wagtailadmin.edit_handlers import MultiFieldPanel, FieldPanel, StreamFieldPanel
from wagtail.wagtailimages.blocks import ImageChooserBlock
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel
from wagtail.wagtailembeds.blocks import EmbedBlock
from wagtail.wagtailembeds.format import embed_to_frontend_html
from wagtail.wagtailembeds.embeds import get_embed
from wagtail.wagtailembeds.exceptions import EmbedException
from wagtail.contrib.wagtailroutablepage.models import RoutablePageMixin, route
from wagtail.contrib.wagtailfrontendcache.utils import purge_page_from_cache
from modelcluster.fields import ParentalKey
from modelcluster.contrib.taggit import ClusterTaggableManager
from taggit.models import TaggedItemBase

class MarkdownBlock(blocks.TextBlock):
    class Meta:
        template = 'kakera_blog/blocks/markdown.html'

class SteamWidgetBlock(blocks.IntegerBlock):
    class Meta:
        template = 'kakera_blog/blocks/steam.html'
        icon = 'site'

class DefaultStreamBlock(blocks.StreamBlock):
    markdown = MarkdownBlock()
    image = ImageChooserBlock()
    embed = EmbedBlock()
    steam_widget = SteamWidgetBlock(help_text="Enter a Steam ID, eg. to embed Harmonia (https://store.steampowered.com/app/421660), enter: 421660.")

class BlogPageTag(TaggedItemBase):
    content_object = ParentalKey('kakera_blog.BlogPage', related_name='tagged_items')

class BlogPage(RoutablePageMixin, Page):
    published = models.DateTimeField()
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)

    cover_image = models.ForeignKey('kakera_core.CustomImage', null=True, blank=True, on_delete=models.SET_NULL, related_name='+')
    cover_embed = models.CharField(max_length=1000, null=True, blank=True)

    body = StreamField(DefaultStreamBlock())
    tags = ClusterTaggableManager(through=BlogPageTag, blank=True)

    search_fields = Page.search_fields + [
        index.SearchField('title'),
    ]

    content_panels = Page.content_panels + [
        FieldPanel('published'),
        FieldPanel('author'),
        MultiFieldPanel([
            ImageChooserPanel('cover_image'),
            FieldPanel('cover_embed'),
        ], "Cover"),
        StreamFieldPanel('body'),
        FieldPanel('tags'),
    ]

    # Only allow blog posts under index pages, disallow subpages
    parent_page_types = ['kakera_blog.BlogIndexPage']
    subpage_types = []

    # Redirect /edit to the admin edit form.
    @route(r'^edit/$')
    def edit(self, request):
        return redirect('wagtailadmin_pages:edit', self.pk)

    def get_excerpt(self):
        for block in self.body:
            if block.block_type == 'markdown':
                return ' '.join(block.value.split(' ')[:50]) + "..."
        return ""

    def get_embed(self):
        try:
            return get_embed(self.cover_embed)
        except EmbedException:
            return None

    def get_cover_embed_html(self):
        return embed_to_frontend_html(self.cover_embed)

    def get_cover_embed_thumbnail_url(self):
        try:
            return get_embed(self.cover_embed).thumbnail_url
        except EmbedException:
            return ""

    def get_og_type(self):
        return "article"

    def get_twitter_card_type(self):
        if self.cover_embed:
            return "player"
        return "summary_large_image"

def blog_page_changed(page):
    for index_page in BlogIndexPage.objects.ancestor_of(page):
        purge_page_from_cache(index_page)

@receiver(page_published, sender=BlogPage)
def blog_published_handler(instance, **kwargs):
    blog_page_changed(instance)

@receiver(pre_delete, sender=BlogPage)
def blog_deleted_handler(instance, **kwargs):
    blog_page_changed(instance)

class BlogIndexPage(Page):
    parent_page_types = ['wagtailcore.Page']

    def get_context(self, request):
        context = super(BlogIndexPage, self).get_context(request)

        posts = BlogPage.objects.child_of(self).live().select_related('author').order_by('-published')
        pages = Paginator(posts, 12)

        page_nr = request.GET.get('page', 1)
        try:
            page = pages.page(page_nr)
        except PageNotAnInteger:
            page = pages.page(1)
        except EmptyPage:
            page = []
        context['blog_entries'] = page

        return context

class StaticPage(Page):
    cover_image = models.ForeignKey('kakera_core.CustomImage', null=True, blank=True, on_delete=models.SET_NULL, related_name='+')

    body = StreamField(DefaultStreamBlock())

    search_fields = Page.search_fields + [
        index.SearchField('title'),
    ]

    content_panels = Page.content_panels + [
        ImageChooserPanel('cover_image'),
        StreamFieldPanel('body'),
    ]

    def get_excerpt(self):
        for block in self.body:
            if block.block_type == 'markdown':
                return ' '.join(block.value.split(' ')[:50]) + "..."
        return ""

    def get_og_type(self):
        return "article"

    def get_twitter_card_type(self):
        return "summary_large_image"
