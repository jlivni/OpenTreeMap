from django.conf import settings

def site_root(context):
    return {
        'GEOSERVER_GEO_LAYER': settings.GEOSERVER_GEO_LAYER,
        'GEOSERVER_GEO_STYLE': settings.GEOSERVER_GEO_STYLE,
        'SITE_ROOT': settings.SITE_ROOT,
        'SITE': settings.SITE,
        'STATIC_URL': settings.STATIC_URL,
        'GEOSERVER_URL': settings.GEOSERVER_URL,
        'TILECACHE_URL': settings.TILECACHE_URL,
        'TILECACHE_LAYER': settings.TILECACHE_LAYER }
