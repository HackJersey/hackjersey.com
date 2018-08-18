from django.conf.urls import include, url
from django.conf import settings
from django.urls import path, re_path
from project.apps.boundary import views

urlpatterns = [
    re_path(r'.*', views.redirect_view),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns