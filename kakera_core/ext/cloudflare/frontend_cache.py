import logging
from urllib.parse import urlparse

from wagtail.wagtailcore.models import Site
from wagtail.contrib.wagtailfrontendcache.backends import CloudflareBackend as BaseCloudflareBackend

logger = logging.getLogger(__name__)

def zone_id_for_url(url):
    parts = urlparse(url)
    try:
        site = Site.objects.get(hostname=parts.hostname)
    except Site.DoesNotExist:
        return ""

    settings = site.settings.first()
    return "" if not settings else settings.cloudflare_zone_id

class CloudflareBackend(BaseCloudflareBackend):
    def __init__(self, params):
        self.cloudflare_email = params.pop('EMAIL')
        self.cloudflare_token = params.pop('TOKEN')

    def purge(self, url):
        if not self.cloudflare_token:
            return

        zone_id = zone_id_for_url(url)
        logger.info("zone=%s for url=%s", zone_id, url)
        if zone_id:
            backend = BaseCloudflareBackend({
                'EMAIL': self.cloudflare_email,
                'TOKEN': self.cloudflare_token,
                'ZONEID': zone_id,
            })
            backend.purge(url.replace('https://', 'http://'))
            backend.purge(url.replace('http://', 'https://'))
