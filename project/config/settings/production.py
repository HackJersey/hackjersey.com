from project.common import *

#RabbitMQ/Celery settings
BROKER_URL = 'amqp://gkhrpumf:mY0nLF7_vPmEg_vlrmFy2l5rvaDnAeL5@elephant.rmq.cloudamqp.com/gkhrpumf'

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('CRIME_SECRET_KEY')

SECURE_HSTS_SECONDS = 31536000
SESSION_COOKIE_SECURE = True

LOGGING['django.request'] = {
            'handlers': ['mail_admins'],
            'level': 'WARNING',
            'propagate': True,
        }
