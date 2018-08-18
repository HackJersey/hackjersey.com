from django.conf.urls import include, url
from django.contrib import flatpages
from django.contrib.flatpages import views
from django.conf import settings
from django.urls import path, re_path
from django.contrib.auth import views as auth_views
from django.views.generic.base import RedirectView
from tastypie.api import Api
from project.apps.boundary import views

urlpatterns = [
    #path('', views.index),
    #path('<path:url>', views.flatpage),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns