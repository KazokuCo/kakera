from django.db import models

from wagtail.wagtailcore.models import Page
from wagtail.wagtailcore.fields import StreamField
from wagtail.wagtailcore.blocks import TextBlock
from wagtail.wagtailsearch import index
from wagtail.wagtailadmin.edit_handlers import FieldPanel, StreamFieldPanel
from wagtail.wagtailimages.blocks import ImageChooserBlock
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel
from wagtail.wagtailembeds.blocks import EmbedBlock

class MarkdownBlock(TextBlock):
	class Meta:
		template = 'kakera_blog/blocks/markdown.html'

class BlogPage(Page):
	published = models.DateTimeField()
	
	cover_image = models.ForeignKey('wagtailimages.Image', null=True, blank=True, on_delete=models.SET_NULL, related_name='+')
	
	intro = models.CharField(max_length=250)
	body = StreamField([
		('markdown', MarkdownBlock()),
		('image', ImageChooserBlock()),
		('embed', EmbedBlock()),
	])
	
	search_fields = Page.search_fields + [
		index.SearchField('title'),
		index.SearchField('intro'),
	]
	
	content_panels = Page.content_panels + [
		FieldPanel('published'),
		ImageChooserPanel('cover_image'),
		FieldPanel('intro'),
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
