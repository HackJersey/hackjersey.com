from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.contrib.sites.models import Site
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.conf import settings
import datetime

from project.apps.crime.models import Release

def index(request):
    now = datetime.datetime.now()
    return render(request, 'crime/index.html')

def pdf_release_listing(request):
    now = datetime.datetime.now()
    data_releases = Release.objects.filter(file_type="1").order_by('-date_released')
    paginator = Paginator(data_releases, 50)
    page = request.GET.get('page')
    releases = paginator.get_page(page)
    return render(request, 'crime/pdf_releases.html', {'releases': releases,
                                                'base_url':settings.AWS_S3_CUSTOM_DOMAIN})
def csv_release_listing(request):
    now = datetime.datetime.now()
    data_releases = Release.objects.filter(file_type="2").order_by('-date_released')
    paginator = Paginator(data_releases, 50)
    page = request.GET.get('page')
    releases = paginator.get_page(page)
    return render(request, 'crime/pdf_releases.html', {'releases': releases,
                                                'base_url':settings.AWS_S3_CUSTOM_DOMAIN})

def redirect_view(request):
    path = "/crime{0}".format(request.path)
    site_id = Site.objects.all().order_by('id').first().domain
    redirect_url = "http://{0}{1}".format(site_id, path)
    return redirect(redirect_url)