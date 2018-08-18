from django_hosts import patterns, host

host_patterns = patterns('',
    host(r'^www', 'project.urls', name='home'),
    host(r'^crime', 'project.apps.crime.redirect_urls', name='crime'),
    host(r'^boundary', 'project.apps.boundary.redirect_urls', name='boundary'),
)