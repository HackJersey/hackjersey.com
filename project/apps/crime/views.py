from django.shortcuts import render
from django.http import HttpResponse
import datetime

from project.apps.crime.models import Release

def index(request):
    now = datetime.datetime.now()
    data_releases = Release.objects.all()
    return render(request, 'crime/releases.html', {'releases': data_releases})

