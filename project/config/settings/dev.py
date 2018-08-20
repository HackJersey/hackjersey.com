from project.common import *

DEBUG = os.environ.get('DJANGO_DEBUG')
TEMPLATES_DEBUG = DEBUG

INTERNAL_IPS = ('0.0.0.0','127.0.0.1',
	'crime.localhj.app', 'boundary.localhj.app',
	'www.localhj.app')

MIDDLEWARE += ('debug_toolbar.middleware.DebugToolbarMiddleware',)
INSTALLED_APPS += ('debug_toolbar', )


DEBUG_TOOLBAR_CONFIG = {
    'DISABLE_PANELS': [
        'debug_toolbar.panels.redirects.RedirectsPanel',
    ],
    'SHOW_TEMPLATE_CONTEXT': True,
}

#RabbitMQ/Celery settings
BROKER_URL = 'amqp://devuser:devpassword@localhost:5672/myvhost'

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('CRIME_SECRET_KEY')

#settings for SSL and HSTS 
#https://docs.djangoproject.com/en/1.8/ref/middleware/#django.middleware.security.SecurityMiddleware
#SECURE_SSL_REDIRECT = False #this is handled by the secure proxy ssl header above. 
#Setting it to true will result in infinite redirects/worker timeouts

SECURE_HSTS_SECONDS = 360
SESSION_COOKIE_SECURE = False