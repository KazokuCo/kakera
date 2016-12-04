from django.db import models
from django.contrib.auth.models import AbstractUser
from wagtail.wagtailadmin.edit_handlers import FieldPanel
from wagtail.wagtailsnippets.models import register_snippet
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel

class User(AbstractUser):
    bio = models.TextField(blank=True)
    twitter = models.CharField(max_length=15, blank=True)

@register_snippet
class Theme(models.Model):
    name = models.CharField(max_length=250)
    site = models.ForeignKey('wagtailcore.Site', on_delete=models.PROTECT, related_name='themes')
    active = models.BooleanField(default=False)

    logo = models.ForeignKey('wagtailimages.Image', null=True, blank=True, on_delete=models.SET_NULL, related_name='+')
    cover = models.ForeignKey('wagtailimages.Image', null=True, blank=True, on_delete=models.SET_NULL, related_name='+')
    background = models.ForeignKey('wagtailimages.Image', null=True, blank=True, on_delete=models.SET_NULL, related_name='+')
    extra_css = models.TextField(blank=True)

    panels = [
        FieldPanel('name'),
        FieldPanel('site'),
        FieldPanel('active'),
        ImageChooserPanel('logo'),
        ImageChooserPanel('cover'),
        ImageChooserPanel('background'),
        FieldPanel('extra_css'),
    ]

    def __str__(self):
        return self.name

@register_snippet
class Settings(models.Model):
    site = models.ForeignKey('wagtailcore.Site', on_delete=models.PROTECT, related_name='settings')

    twitter_username = models.CharField(max_length=25, blank=True)
    facebook_username = models.CharField(max_length=25, blank=True)
    patreon_username = models.CharField(max_length=25, blank=True)
    discord_link = models.URLField(max_length=255, blank=True)

    discourse_url = models.URLField(max_length=255, blank=True)

    panels = [
        FieldPanel('site'),
        FieldPanel('twitter_username'),
        FieldPanel('facebook_username'),
        FieldPanel('patreon_username'),
        FieldPanel('discord_link'),
        FieldPanel('discourse_url'),
    ]

    def __str__(self):
        return "Settings for {0}".format(self.site)
