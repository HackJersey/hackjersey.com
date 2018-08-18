from django.contrib.sites.models import Site

def root_url(request):
    home_url = Site.objects.first().domain
    """
    Pass your root_url from the settings.py
    """
    return {'SITE_DOMAIN': home_url}