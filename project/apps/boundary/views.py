from django.contrib.sites.models import Site
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.conf import settings
import datetime

from project.apps.crime.models import Release

def redirect_view(request):
    path = "/boundary{0}".format(request.path)
    site_id = Site.objects.all().order_by('id').first().domain
    redirect_url = "http://{0}{1}".format(site_id, path)
    return redirect(redirect_url)