from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractUser
from wagtail.wagtailadmin.edit_handlers import FieldPanel, MultiFieldPanel
from wagtail.wagtailsnippets.models import register_snippet
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel

def validate_no_at_prefix(value):
    if len(value) >= 1 and value[0] == '@':
        raise ValidationError("please omit the @ prefix")

class User(AbstractUser):
    bio = models.TextField(blank=True)
    twitter = models.CharField(max_length=15, blank=True, validators=[validate_no_at_prefix])

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
    description = models.CharField(max_length=255, blank=True)

    twitter_username = models.CharField(max_length=25, blank=True)
    facebook_username = models.CharField(max_length=25, blank=True)
    facebook_id = models.BigIntegerField(null=True, blank=True)
    facebook_app_id = models.BigIntegerField(null=True, blank=True)
    patreon_username = models.CharField(max_length=25, blank=True)
    discord_link = models.URLField(max_length=255, blank=True)

    discourse_url = models.URLField(max_length=255, blank=True)

    panels = [
        FieldPanel('site'),
        FieldPanel('description'),
        MultiFieldPanel([
            FieldPanel('twitter_username'),
        ], "Twitter"),
        MultiFieldPanel([
            FieldPanel('facebook_username'),
            FieldPanel('facebook_id'),
            FieldPanel('facebook_app_id'),
        ], "Facebook"),
        MultiFieldPanel([
            FieldPanel('patreon_username'),
        ], "Patreon"),
        MultiFieldPanel([
            FieldPanel('discord_link'),
        ], "Discord"),
        MultiFieldPanel([
            FieldPanel('discourse_url'),
        ], "Discourse")
    ]

    def __str__(self):
        return "Settings for {0}".format(self.site)
