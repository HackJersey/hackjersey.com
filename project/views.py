from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
import datetime

from project.apps.crime.models import Release

def index(request):
    now = datetime.datetime.now()
    data_releases = Release.objects.all().order_by()
    return render(request, 'index.html', {'releases': data_releases,
                                                'base_url':settings.AWS_S3_CUSTOM_DOMAIN})

'''
def release_listing(request):
    now = datetime.datetime.now()
    data_releases = Release.objects.all()
    paginator = Paginator(data_releases, 50)
    page = request.GET.get('page')
    releases = paginator.get_page(page)
    return render(request, 'crime/releases.html', {'releases': releases,
                                                'base_url':settings.AWS_S3_CUSTOM_DOMAIN})'''