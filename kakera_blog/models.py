from django.http import HttpResponse
from django.dispatch import receiver
from django.db import models
from django.db.models.signals import pre_delete
from django.conf import settings
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.cache import cache
from django.shortcuts import redirect
from django.template.loader import get_template
from django.utils.feedgenerator import Atom1Feed

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
from wagtailmenus.models import MenuPage
from modelcluster.fields import ParentalKey
from modelcluster.contrib.taggit import ClusterTaggableManager
from taggit.models import TaggedItemBase
from lxml import html

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

class BlogPage(RoutablePageMixin, MenuPage):
    published = models.DateTimeField()
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)

    cover_image = models.ForeignKey('kakera_core.CustomImage', null=True, blank=True, on_delete=models.SET_NULL, related_name='+')
    cover_embed = models.CharField(max_length=1000, null=True, blank=True)

    body = StreamField(DefaultStreamBlock())
    tags = ClusterTaggableManager(through=BlogPageTag, blank=True)

    # Autogenerated from body on save.
    excerpt = models.TextField(blank=True)

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
        return self.excerpt

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

    def save(self, *args, **kwargs):
        cooked = str(get_template("kakera_blog/_blog_page_body.html").render({'page': self}))
        if cooked.strip():
            self.excerpt = ' '.join(html.fromstring(cooked.encode('utf-8'))\
                .text_content().split(' ')[:50]).strip().rstrip('.') + '...'
        else:
            self.excerpt = ""

        super(BlogPage, self).save(*args, **kwargs)

def blog_page_changed(page):
    for index_page in BlogIndexPage.objects.ancestor_of(page):
        purge_page_from_cache(index_page)
    cache.clear()

@receiver(page_published, sender=BlogPage)
def blog_page_published(instance, **kwargs):
    blog_page_changed(instance)

@receiver(pre_delete, sender=BlogPage)
def blog_page_deleted(instance, **kwargs):
    blog_page_changed(instance)

class BlogIndexPage(RoutablePageMixin, MenuPage):
    parent_page_types = ['wagtailcore.Page']

    @route(r'^feed/$')
    def feed(self, request):
        feed = Atom1Feed(
            title=self.title,
            link=self.full_url,
            description="Latest posts from {}".format(self.title),
        )
        for post in self.get_posts().prefetch_related('tagged_items__tag'):
            feed.add_item(
                unique_id=post.slug,
                title=post.title,
                link=post.full_url,
                description=post.excerpt,
                author_name=post.author.get_username(),
                pubdate=post.first_published_at,
                updateddate=post.latest_revision_created_at,
                categories=[t.name for t in post.tags.all()],
            )
        return HttpResponse(
            feed.writeString('utf-8'),
            content_type='text/xml; charset=utf-8',
        )

    def get_context(self, request):
        context = super(BlogIndexPage, self).get_context(request)

        pages = Paginator(self.get_posts(), 12)
        page_nr = request.GET.get('page', 1)
        try:
            page = pages.page(page_nr)
        except PageNotAnInteger:
            page = pages.page(1)
        except EmptyPage:
            page = []
        context['blog_entries'] = page

        return context

    def get_posts(self):
        return BlogPage.objects.child_of(self).live()\
                .select_related('author').order_by('-published')

class StaticPage(RoutablePageMixin, Page):
    cover_image = models.ForeignKey('kakera_core.CustomImage', null=True, blank=True, on_delete=models.SET_NULL, related_name='+')

    body = StreamField(DefaultStreamBlock())
    ordering = models.IntegerField(default=0)

    # Autogenerated from body on save.
    excerpt = models.TextField(blank=True)

    search_fields = Page.search_fields + [
        index.SearchField('title'),
    ]

    content_panels = Page.content_panels + [
        ImageChooserPanel('cover_image'),
        StreamFieldPanel('body'),
    ]

    promote_panels = Page.promote_panels + [
        FieldPanel('ordering'),
    ]

    # Redirect /edit to the admin edit form.
    @route(r'^edit/$')
    def edit(self, request):
        return redirect('wagtailadmin_pages:edit', self.pk)

    def modify_submenu_items(self, menu_items, **_):
        return sorted(menu_items, key=lambda o: o.specific.ordering)

    def get_excerpt(self):
        return self.excerpt

    def get_og_type(self):
        return "article"

    def get_twitter_card_type(self):
        return "summary_large_image"

    def save(self, *args, **kwargs):
        cooked = get_template("kakera_blog/_blog_page_cooked.html").render({'page': self})
        if cooked.strip():
            self.excerpt = ' '.join(html.fromstring(cooked)\
                .text_content().split(' ')[:50]).rstrip('.') + '...'
        else:
            self.excerpt = ""

        super(StaticPage, self).save(*args, **kwargs)

def static_page_changed(page):
    cache.clear()

@receiver(page_published, sender=StaticPage)
def static_page_published(instance, **kwargs):
    static_page_changed(instance)

@receiver(pre_delete, sender=StaticPage)
def static_page_deleted(instance, **kwargs):
    static_page_changed(instance)
