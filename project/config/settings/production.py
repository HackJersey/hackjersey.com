from project.common import *

DEBUG = os.environ.get('DJANGO_DEBUG')
#TODO set this all up

'''
#RabbitMQ/Celery settings
BROKER_URL = 'amqp://poiocqex:wXQyrJ3VlOVtLIlRHEg6KWTa3Jhm2KbH@owl.rmq.cloudamqp.com/poiocqex'
CELERY_TIMEZONE = 'America/New_York'

'''
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('CRIME_SECRET_KEY')

SECURE_HSTS_SECONDS = 31536000
SECURE_FRAME_DENY = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SECURE_HSTS_INCLUDE_SUBDOMAINS = True


LOGGING['django.request'] = {
            'handlers': ['mail_admins'],
            'level': 'WARNING',
            'propagate': True,
        }
