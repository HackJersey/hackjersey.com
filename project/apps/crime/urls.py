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

v1_api = Api(api_name='v1')
v1_api.register(ReleaseResource())
v1_api.register(AgencyResource())
v1_api.register(CityResource())
v1_api.register(CountyResource())

urlpatterns = [
    #path('', views.index),
    path('releases/pdf/', views.pdf_release_listing),
    path('releases/csv/', views.csv_release_listing),
    path('api/', include(v1_api.urls)),
    #path('tinymce/', include('tinymce.urls')),
    #re_path(r'favicon\.ico$', RedirectView.as_view(url=settings.STATIC_URL+'favicon.ico', permanent=True)),
    #path('selectable/', include('selectable.urls')),
    #path('<path:url>', views.flatpage),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns