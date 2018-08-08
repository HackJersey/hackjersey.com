# coding: utf-8
from datetime import datetime, date
import io
import re
from urllib.parse import urlparse

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.text import slugify
from django.contrib.postgres.fields import JSONField

from phonenumber_field.modelfields import PhoneNumberField
import pytz
from timezone_field import TimeZoneField
import requests

from sortedm2m.fields import SortedManyToManyField
from url_or_relative_url_field.fields import URLOrRelativeURLField

import pdfplumber

class State(models.Model):
    name = models.CharField(max_length=100)
    abbrev = models.CharField(max_length=50, blank=True, null=True, unique=True)
    fips = models.CharField(max_length=10, blank=True, null=True, unique=True)
    assoc_press = models.CharField(max_length=25, blank=True, null=True)
    census_division_name = models.CharField(max_length=100, blank=True, null=True)
    standard_federal_region = models.CharField(max_length=50, blank=True, null=True)
    census_region_name = models.CharField(max_length=50, blank=True, null=True)
    census_region = models.CharField(max_length=25, blank=True, null=True)
    circuit_court = models.CharField(max_length=15, blank=True, null=True)
    census_division = models.CharField(max_length=50, blank=True, null=True)

    def __unicode__(self):
        return u'{0}'.format(self.name)

    def __str__(self):
        return u'{0}'.format(self.name)

class County(models.Model):
    name = models.CharField(max_length=100)
    state = models.ForeignKey(State, on_delete=models.PROTECT)
    abbrev = models.CharField(max_length=50, blank=True, null=True)
    fips = models.CharField(max_length=10, blank=True, null=True, unique=True)
    GNIS = models.CharField(max_length=30, blank=True, null=True)
    msa = models.CharField(max_length=30, blank=True, null=True)

    class Meta:
        verbose_name_plural = "counties"

    def __unicode__(self):
        return u'{0}, {1}'.format(self.name, self.state.abbrev)

    def __str__(self):
        return u'{0}, {1}'.format(self.name, self.state.abbrev)

class City(models.Model):
    name = models.CharField(max_length=100)
    county = models.ForeignKey(County, on_delete=models.PROTECT)
    abbrev = models.CharField(max_length=50, blank=True, null=True)
    fips = models.CharField(max_length=50, blank=True, null=True)
    muni_type = models.CharField(max_length=100, blank=True, null=True)
    character = models.CharField(max_length=100, blank=True, null=True)
    nj_muncode = models.CharField(max_length=30, blank=True, null=True)
    msa = models.CharField(max_length=30, blank=True, null=True)
    state_code_1968 = models.CharField(max_length=30, blank=True, null=True)
    Treasury_Taxation_code_03 = models.CharField(max_length=30, blank=True, null=True)
    Federal_code_03 = models.CharField(max_length=30, blank=True, null=True)
    Alternate_County_Code_state = models.CharField(max_length=30, blank=True, null=True)
    GNIS = models.CharField(max_length=30, blank=True, null=True)
    SSN = models.CharField(max_length=30, blank=True, null=True)
    OGIS_MUN_CODE = models.CharField(max_length=30, blank=True, null=True)

    class Meta:
        verbose_name_plural = "cities"

    def __unicode__(self):
        return u'{0}, {1}'.format(self.name, self.county.state.abbrev)

    def __str__(self):
        return u'{0}, {1}'.format(self.name, self.county.state.abbrev)

class Agency(models.Model):
    AGENCY_CHOICES = (
        ("1", "local"),
        ("2", "county"),
        ("3", "state"),
        ("4", "federal"),
        ("5", "special"),
        )
    
    name = models.CharField(max_length=200)
    street_number = models.CharField(null=True, blank=True, max_length=50)
    street_name = models.CharField(null=True, blank=True, max_length=200)
    room = models.CharField(null=True, blank=True, max_length=50)
    city = models.ForeignKey(City, null=True, blank=True, related_name='agency', on_delete=models.SET_NULL)
    state_name = models.ForeignKey(State, related_name='agency2', verbose_name="state", on_delete=models.PROTECT)
    zip_code = models.CharField(null=True, blank=True, max_length=30, verbose_name="zip")
    website = URLOrRelativeURLField(null=True, blank=True)
    agency_notes = models.TextField(blank=True, null=True, verbose_name = "Notes about agency")
    agency_type = models.CharField(choices=AGENCY_CHOICES, max_length=10, blank=False, default="1")
    cities = models.ManyToManyField(City, related_name='cities_covered', verbose_name="cities in jurisdiction")
    counties = models.ManyToManyField(County, related_name = 'counties_covered', verbose_name="counties covered")
    ori7 = models.CharField(max_length=20, null=True, blank=True, help_text="Federal ORI ID number for the jurisdiciton")
    ori9 = models.CharField(max_length=20, null=True, blank=True, help_text="Federal ORI ID number for the jurisdiciton")

    class Meta:
        verbose_name_plural = "agencies"
        ordering=('name',)

    def __unicode__(self):
        return u'{0}'.format(self.name)

    def __str__(self):
        return u'{0}'.format(self.name)

class Release(models.Model):
    #a model for the raw, original data release, usually a PDF
    FORMAT_CHOICES = (
        ("1", "PDF"),
        ("2", "csv"),
        )

    PERIOD_CHOICES = (
        ("1", "monthly"),
        ("2", "quarterly"),
        ("3", "annual"),
        )

    file_name = models.CharField(max_length=100)
    file_type = models.CharField(choices = FORMAT_CHOICES, max_length=10, blank=True, null=True)
    hj_url = URLOrRelativeURLField(unique=True, verbose_name="URL", blank=True, null=True)
    length = models.SmallIntegerField(blank=True, null=True, help_text="Number of pages if a PDF or records if CSV")
    date_released = models.DateField(blank=True, null=True, verbose_name = "Date of data release")
    date_collected = models.DateField(blank=True, null=True, verbose_name="Date downloaded")
    year_of_data = models.SmallIntegerField(blank=True, null=True, help_text="year the data covers")
    frequency_type = models.CharField(choices = PERIOD_CHOICES, max_length=10, blank=False)
    data_source = models.ForeignKey(Agency, null=True, blank=True, related_name='source_agency', help_text="Source Agency", on_delete=models.SET_NULL)

    class Meta:
        verbose_name_plural="Releases"

    def __unicode__(self):
        return u"{0}".format(self.file_name)

    def __str__(self):
        return u"{0}".format(self.file_name)

    def request_release_url(self, url):
        url = url.strip()
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
        r = requests.get(url, headers=headers)
        if r.ok:
            return r.content, url
        else:
            print("{0}: {1} is not found on s3".format(r.status_code, url))
            return None, url

    def check_pdf_length(self, pdf_file, url):
        try:
            with io.BytesIO(pdf_file) as open_pdf_file:
                read_pdf = pdfplumber.load(open_pdf_file)
                num_pages = len(read_pdf.pages)
                length = num_pages
                self.length = length
        except:
            print("{0} is not a pdf".format(url))
            length = None
            return
        return length

    def release_name_parser(self, url, length=None):
        annuals = {'https://s3.amazonaws.com/njsp-crime-reports/pdfs/20150605_crimetrend.pdf':'2014',
        'https://s3.amazonaws.com/njsp-crime-reports/pdfs/20150612_crimetrend.pdf':'2014',
        'https://s3.amazonaws.com/njsp-crime-reports/pdfs/20151015_crimetrend.pdf':'2014',
        'https://s3.amazonaws.com/njsp-crime-reports/pdfs/20160129_crimetrend.pdf':'2015',
        'https://s3.amazonaws.com/njsp-crime-reports/pdfs/20170106_crimetrend.pdf':'2016',
        'https://s3.amazonaws.com/njsp-crime-reports/pdfs/20170113_crimetrend.pdf':'2016',
        'https://s3.amazonaws.com/njsp-crime-reports/pdfs/20170120_crimetrend.pdf':'2016',
        'https://s3.amazonaws.com/njsp-crime-reports/pdfs/20170127_crimetrend.pdf':'2016',
        'https://s3.amazonaws.com/njsp-crime-reports/pdfs/20170203_crimetrend.pdf':'2016',
        'https://s3.amazonaws.com/njsp-crime-reports/pdfs/20180116_crimetrend.pdf':'2017',
        'https://s3.amazonaws.com/njsp-crime-reports/pdfs/20180123_crimetrend.pdf':'2017',
        'https://s3.amazonaws.com/njsp-crime-reports/pdfs/20180129_crimetrend.pdf':'2017',
        'https://s3.amazonaws.com/njsp-crime-reports/pdfs/20180202_crimetrend.pdf':'2017'}
        url = url.strip()
        file_type = url.split('.')[-1]
        if file_type.lower() == "pdf":
            file_type="1"
        elif file_type.lower() == "csv":
            file_type="2"
        else:
            file_type = None
        if length:
            self.length = length
        else:
            length = self.check_pdf_length(url)
        hj_url = urlparse(url).path
        file_name = hj_url.split('/')[-1].strip()
        date_released = date(int(file_name[:4]),
                            int(file_name[4:6]), 
                            int(file_name[6:8]))
        if "qtr" in file_name:
            frequency_type = "2"
            year_of_data = int(file_name.split('.')[0][-4:])
        elif "ucr" in file_name:
            frequency_type = "3"
            year_of_data = int(file_name.split('_')[-1][:4])
        elif '_crimetrend' in file_name:
            if file_name in annuals.keys():
                frequency_type = "3"
                year_of_data = annual_keys[file_name]
            else:
                #any file that says _2016_crimetrend.pdf or 
                #crimetrend_2017.pdf is an annual.
                #beware, many of the monthlies in 2018 end with
                #crimetrend_2018.
                regex = re.compile(r'_2016|7')
                if regex.search(file_name):
                    frequency_type = "3"
                else:
                    frequency_type = "1"
            regex = re.compile(r'_(\d{4})')
            try:
                year_of_data = regex.search(file_name).groups()[0]
            except:
                year_of_data = file_name[:4]
        self.file_name = file_name
        self.file_type = file_type
        self.hj_url = hj_url
        self.date_released = date_released
        self.year_of_data = year_of_data
        self.frequency_type = frequency_type
        return (file_name, file_type, hj_url, length,
            date_released, year_of_data, frequency_type)

    #def fetcher(self)
        #TODO
        #return
        #add date collected in fetcher


class TaskHistory(models.Model):
    name = models.CharField(max_length=100, verbose_name="Task name", help_text="Select a task to record.")
    history = JSONField(default={}, verbose_name="History", help_text="JSON containing the tasks history.")

    class Meta:
        verbose_name="Task History"
        verbose_name_plural="Task Histories"

    def __unicode__(self):
        return u"Task History of Task: {0}".format(self.name)

    def __str__(self):
        return u"Task History of Task: {0}".format(self.name)


class HJUser(models.Model):
    TZ_CHOICES = [(tz, tz) for tz in pytz.country_timezones['US']]

    user = models.OneToOneField(User, on_delete=models.PROTECT)
    title = models.CharField(max_length=100, blank=True, null=True)
    cell = PhoneNumberField(blank=True, null=True)
    other_phone = PhoneNumberField(blank=True, null=True)
    twitter = models.CharField(max_length=50, blank=True, null=True)
    last_update = models.DateTimeField(blank=True, null=True)
    tz = TimeZoneField(blank=True, null=True, choices=TZ_CHOICES, verbose_name='Time Zone')

    class Meta:
        verbose_name = "HJ user"

    def __unicode__(self):
        return u'{0} {1}'.format(self.user.first_name, self.user.last_name)

    def __str__(self):
        return u'{0} {1}'.format(self.user.first_name, self.user.last_name)


class Documentation(models.Model):
    HELP_CHOICES = (
        ("admin", "admin"),
        ("public", "public"),
        )

    slug = models.SlugField(max_length=200, unique=True, blank=True, null=True)
    title = models.CharField(max_length=200)
    text = models.TextField(blank=True, null=True)
    chapter = models.SmallIntegerField(blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)
    help_type = models.CharField(choices=HELP_CHOICES, default="admin", max_length=100, blank=True, null=True)

    class Meta:
        verbose_name_plural="Documentation"

    def __unicode__(self):
        return u'{0}'.format(self.title)

    def __str__(self):
        return u'{0}'.format(self.title)

    def save(self):
        title = self.title
        self.slug = slugify(title)
        super(Documentation, self).save()


#FUTURE TODO
#add tweet models