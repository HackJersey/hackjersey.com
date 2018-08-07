import io
import urllib
from datetime import date
import os
import logging
import requests
from django.core.management.base import BaseCommand, CommandError
from project.apps.crime.models import Agency, Release

import pdfplumber

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = "Load the releases the first time."

    def open_releases_file(self):
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        file_location = BASE_DIR+ "../../../../../scraper/data/pdfs/crime_reports.csv"
        with open(file_location, 'rU') as f:
            row_list = f.readlines()
        return row_list

    def create_release_objects(self, row_list):
        counter = 0
        row_list = row_list[1:]
        for row in row_list:
            p = Release()
            p.data_source = Agency.objects.get(ori7 = "NJNSP00")
            length = p.check_pdf_length(row.strip())
            if not length:
                print("{0} is missing from s3".format(row))
                continue
            (file_name, file_type, hj_url, length,
                date_released, year_of_data, 
                time_period_covered) = p.release_name_parser(row.strip(), length)
            p.save()
            counter+=1
        return counter

    def handle(self, *args, **options):
        """
        load all the preliminary geographical data
        """
        logger.debug("opening state list from the state_table.csv")
        release_list = self.open_releases_file()
        counter = self.create_release_objects(release_list)
        logger.debug("Loaded {0} state records".format(counter))
