import os
import logging
import requests
from django.core.management.base import BaseCommand, CommandError
from django.contrib.sites.models import Site
from project.apps.crime.models import Release

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = "Add quarters field data to quarterly releases."

    def update_quarterlies(self):
        quarterlies = Release.objects.filter(frequency_type="2")
        report_list = []
        for report in quarterlies:
            if "_1st" in report.file_name:
                report.quarter = 1
            elif "_2nd" in report.file_name:
                report.quarter = 2
            elif "_3rd" in report.file_name:
                report.quarter = 3
            elif "_4th"in report.file_name:
                report.quarter = 4
            report.save()
            report_list.append(report)
        return report_list


    def handle(self, *args, **options):
        """
        load all the preliminary geographical data
        """
        logger.debug("adding quarterly data to my Release models")
        report_list = self.update_quarterlies()
        print("updated {0} records".format(len(report_list)))
        logger.debug("Updated {0} records".format(len(report_list)))