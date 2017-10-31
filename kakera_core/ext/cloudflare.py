import logging
from urllib.parse import urlparse
from django.conf import settings
from CloudFlare import CloudFlare
from wagtail.wagtailcore.models import Site

logger = logging.getLogger(__name__)

def get_client():
    conf = settings.CLOUDFLARE
    return CloudFlare(
        email=conf.get('EMAIL', None),
        token=conf.get('TOKEN', None),
    ) if conf.get('EMAIL', None) else None

def get_zone_id_for_site(site):
    site_settings = site.settings.first()
    return "" if not site_settings else site_settings.cloudflare_zone_id

def get_zone_id_for_url(url):
    parts = urlparse(url)
    try:
        site = Site.objects.get(hostname=parts.hostname)
        return get_zone_id_for_site(site)
    except Site.DoesNotExist:
        return ""

def urls_with_both_protocols(urls):
    newurls = []
    for url in urls:
        newurls.append(url.replace('https://', 'http://'))
        newurls.append(url.replace('http://', 'https://'))
    return newurls

def purge_urls(urls):
    purged_urls = urls_with_both_protocols(urls)
    for url in purged_urls:
        logger.info("[cloudflare] purging: %s", url)

    zone_id = get_zone_id_for_url(urls[0])
    cf = get_client()
    if not zone_id or not cf:
        return

    cf.zones.purge_cache.delete(zone_id, data={'files': purged_urls})

def purge_site(site):
    zone_id = get_zone_id_for_site(site)
    cf = get_client()
    if not zone_id or not cf:
        return

    cf.zones.purge_cache.delete(zone_id, data={'purge_everything': True})
