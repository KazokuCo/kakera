import scipy
import scipy.misc
import scipy.cluster
from django.db import models
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from django.core.cache import cache
from django.contrib.auth.models import AbstractUser
from wagtail.wagtailcore.models import Site
from wagtail.wagtailadmin.edit_handlers import FieldPanel, MultiFieldPanel
from wagtail.wagtailsnippets.models import register_snippet
from wagtail.wagtailimages.models import Image as BaseImage, AbstractImage, AbstractRendition
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel
from kakera_core.ext.cloudflare import purge_site

def validate_no_at_prefix(value):
    if len(value) >= 1 and value[0] == '@':
        raise ValidationError("please omit the @ prefix")

class User(AbstractUser):
    bio = models.TextField(blank=True)
    twitter = models.CharField(max_length=15, blank=True, validators=[validate_no_at_prefix])



class CustomImage(AbstractImage):
    color = models.CharField(max_length=6, blank=True)
    admin_form_fields = BaseImage.admin_form_fields

    def save(self, *args, **kwargs):
        with self.get_willow_image() as willow:
            if willow.has_alpha():
                self.color = ""
            else:
                img = willow.get_pillow_image().resize((150,150)).convert('RGB')
                ar = scipy.misc.fromimage(img)
                ar = ar.reshape(scipy.product(ar.shape[:2]), ar.shape[2]).astype(float)
                color = (scipy.cluster.vq.kmeans2(ar, 1, minit='points')[0]).astype(int)[0]
                self.color = "{:02x}{:02x}{:02x}".format(*color)

        super(CustomImage, self).save(*args, **kwargs)

class CustomRendition(AbstractRendition):
    image = models.ForeignKey(CustomImage, related_name='renditions')

    def aspect_ratio(self):
        return self.height / self.width

    def aspect_ratio_pct(self):
        return int(self.aspect_ratio() * 100)

    class Meta:
        unique_together = (
            ('image', 'filter_spec', 'focal_point_key'),
        )

@receiver(post_delete, sender=CustomImage)
def image_delete(sender, instance, **kwargs):
    instance.file.delete(False)

@receiver(post_delete, sender=CustomRendition)
def rendition_delete(sender, instance, **kwargs):
    instance.file.delete(False)



@register_snippet
class Theme(models.Model):
    name = models.CharField(max_length=250)
    site = models.ForeignKey('wagtailcore.Site', on_delete=models.PROTECT, related_name='themes')
    active = models.BooleanField(default=False)

    logo = models.ForeignKey('kakera_core.CustomImage', null=True, blank=True, on_delete=models.SET_NULL, related_name='+')
    cover = models.ForeignKey('kakera_core.CustomImage', null=True, blank=True, on_delete=models.SET_NULL, related_name='+')
    background = models.ForeignKey('kakera_core.CustomImage', null=True, blank=True, on_delete=models.SET_NULL, related_name='+')
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

@receiver(post_save, sender=Theme)
def theme_save(sender, instance, **kwargs):
    purge_site(instance.site)
    cache.clear()



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

    cloudflare_zone_id = models.CharField(max_length=32, blank=True)
    google_analytics_id = models.CharField(max_length=255, blank=True)

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
        ], "Discourse"),
        MultiFieldPanel([
            FieldPanel('cloudflare_zone_id'),
        ], "Cloudflare"),
        MultiFieldPanel([
            FieldPanel('google_analytics_id'),
        ], "Google Analytics"),
    ]

    def __str__(self):
        return "Settings for {0}".format(self.site)

@receiver(post_save, sender=Theme)
def theme_save(sender, instance, **kwargs):
    purge_site(instance.site)
    cache.clear()

from wagtailmenus import models as menumodels
menu_models = [
    menumodels.Menu, menumodels.MainMenu, menumodels.FlatMenu,
    menumodels.MenuItem, menumodels.MainMenuItem, menumodels.FlatMenuItem,
]
for model in menu_models:
    @receiver(post_save, sender=model)
    def theme_model_save(sender, instance, **kwargs):
        # TODO: Figure out which site was actually changed >_>
        for site in Site.objects.all():
            purge_site(site)
        cache.clear()
