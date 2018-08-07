"""crime URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.contrib import admin
from django.contrib import flatpages
from django.contrib.flatpages import views
from django.conf import settings
from django.urls import path, re_path
from django.contrib.auth import views as auth_views
from django.views.generic.base import RedirectView
from tastypie.api import Api
from project.apps.crime import views
from project.apps.crime.api.resources import (ReleaseResource, AgencyResource,
                                            CityResource, CountyResource)
from project.apps.crime.admin import admin_site


#from . import views
admin.autodiscover()

v1_api = Api(api_name='v1')
v1_api.register(ReleaseResource())
v1_api.register(AgencyResource())
v1_api.register(CityResource())
v1_api.register(CountyResource())


urlpatterns = [
    path('', views.index),
    #path('admin/', admin.site.urls),
    path('pages/', include('django.contrib.flatpages.urls')),
    path('api/', include(v1_api.urls)),
    path('admin/password_reset/', auth_views.password_reset, name='admin_password_reset'),
    path('admin/password_reset/done/', auth_views.password_reset_done, name='password_reset_done'),
    re_path('reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>.+)/$', auth_views.password_reset_confirm, name='password_reset_confirm'),
    path('reset/done/', auth_views.password_reset_complete, name='password_reset_complete'),
    #path('tinymce/', include('tinymce.urls')),
    path('admin/', admin_site.urls),
    #re_path(r'favicon\.ico$', RedirectView.as_view(url=settings.STATIC_URL+'favicon.ico', permanent=True)),
    path('robots.txt', RedirectView.as_view(url=settings.STATIC_URL+'robots.txt', permanent=True)),
    #path('selectable/', include('selectable.urls')),
    #path('<path:url>', views.flatpage),
]


if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns