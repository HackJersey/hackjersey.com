import os
import json
from celery.task.schedules import crontab
from celery.decorators import task, periodic_task
from celery.utils.log import get_task_logger
from datetime import timedelta, datetime
from time import sleep
from django.utils import timezone
from django.conf import settings
from django.core.mail import send_mail
from project.apps.crime.models import Release
from project.apps.crime.utils import compare_urls

from pytz import timezone as ptimezone
import requests

logger = get_task_logger(__name__)

@periodic_task(run_every=(crontab(hour="8", minute="00", day_of_week="*")), ignore_result=True)
def long_wait_task():
    logger.info("Start task")
    today = timezone.localdate()
    last_release = Release.objects.all().order_by('-date_released').first().date_released
    diff = today-last_release
    if diff.days>13:
        admin_addresses = []
        for address in settings.ADMINS:
            admin_addresses.append(address[1])
        result_message = "It has been {0} days since the last NJSP data release. Is there an update? https://www.njsp.org/ucr/current-crime-data1.shtml?agree=0".format(diff.days)
        send_mail('[CRIME] No recent updates', result_message, settings.DEFAULT_FROM_EMAIL, admin_addresses, fail_silently=False)
    else:
        result_message = "The last NJSP UCR update was {0} days ago on {1}".format(diff.days, last_release)
    print(result_message)
    logger.info("Task finished: result = {0}".format(result_message))
    return

@periodic_task(run_every=(crontab(hour="*", minute="01, 21, 41", day_of_week="*")), ignore_result=True)
def scraper_check():
    compare_urls.main()
    return



# A periodic task that will run every minute (the symbol "*" means every)
'''
@periodic_task(run_every=(crontab(hour="*", minute="*", day_of_week="*")), ignore_result=True)
def testing_example():
    logger.info("Start task")
    now = datetime.now()
    date_now = now.strftime("%d-%m-%Y %H:%M:%S")
    result = str(now.day)
    print('Today is now {0} on {1}'.format(now, result))

    logger.info("Task finished: result = {0}".format(result))
    return
'''