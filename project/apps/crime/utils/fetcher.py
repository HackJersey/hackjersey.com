#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
from urllib.parse import *
import calendar, time
from datetime import date, datetime, timedelta
from django.core.files.storage import default_storage

from project.apps.crime.models import Release, Agency

import requests
from lxml import html

class PDFReport:
    def __init__(self, url):
        self.orig_njsp_url = url
        self.final_hj_url = url
        self.hj_filename = urlparse(url).path.split('/')[-1]
        self.s3_file_name = "pdfs/{0}".format(self.hj_filename)
        self.downloaded_file = None

class CrimeUpdate:
    def __init__(self, url='http://www.njsp.org/ucr/current-crime-data1.shtml?agree=0', scrape_date=None):
        self.url = url
        if scrape_date:
            scrape_year=int(scrape_date[:4])
            scrape_month = int(scrape_date[4:6])
            scrape_day = int(scrape_date[-2:])
            scrape_date = date(scrape_year, scrape_month, scrape_day)
            self.date=scrape_date
        else:
            self.date = date.today()
        self.pdf_reports = []

    def add(self, file):
        '''
        Add a new file url to the update list.
        '''
        self.pdf_reports.append(file)

    def update_url(self, url):
        '''
        Update the URL if a user passes in a command-line argument specifying a non-default URL.
        '''
        self.url = url

    def scrape(self):
        '''
        Scrape each the page to get the urls of the items we need to download
        '''
        r = requests.get(self.url, verify=False)
        if not r.ok:
            print("Invalid URL. Please specify a valid URL to scrape with the -u flag.")
            exit()
        else:
            page_html = r.content
        tree = html.fromstring(page_html)
        all_links = tree.xpath('//a/@href')
        page_base_url = "http://www.njsp.org/ucr/"

        for link in all_links:
            if link.endswith('html'):
                #print('skipping {0}'.format(link))
                continue
            elif link.endswith('/'):
                #print('skipping {0}'.format(link))
                continue
            elif link.endswith('pdf'):
                today_string = datetime.strftime(self.date, '%Y%m%d')
                if today_string in link:
                    link = page_base_url+link
                    new_report = PDFReport(link)
                    self.add(new_report)
                else:
                    print('skipping {0}'.format(link))
        return

    def download(self):
        counter = 0
        for pdf in self.pdf_reports:
            r = requests.get(pdf.orig_njsp_url, verify=False)
            pdf.downloaded_file = r.content
            local_name = 'downloads/{0}'.format(pdf.hj_filename)
            with open(local_name, 'wb') as f:
               f.write(pdf.downloaded_file)
            print('Downloaded {0}'.format(local_name))
            counter+=1
        print('Downloaded {0} files from NJSP.'.format(counter))
        return

def main(scrape_date=None, url=None):
    '''
    go to the page, scrape the new files, upload them to s3 and add them to our database
    '''
    if url:
        conf = CrimeUpdate(url = url, scrape_date=scrape_date)
    else:
        conf = CrimeUpdate(scrape_date=scrape_date)
    #scrape out the urls of the new files and save them to conf object
    conf.scrape()
    conf.download()
    if len(conf.pdf_reports)>0:
        for pdf in conf.pdf_reports:
            #create a release object for our database
            p = Release()
            file_name = pdf.hj_filename
            #check our models to ensure it doesn't exist
            existing_model = Release.objects.filter(file_name=file_name)
            #if it's in our db, check s3
            if existing_model.count() > 0:
                on_s3 = default_storage.exists(pdf.s3_file_name)
                if on_s3:
                    print('{0} this file is already on s3'.format(pdf.hj_filename))
                    print('{0} This file is already in our database'.format(pdf.hj_filename))
                    print('adjusting filename')
                    timestamp = calendar.timegm(time.gmtime())
                    pdf.hj_filename = "{0}{1}.pdf".format(pdf.hj_filename.split('.')[0],timestamp)
                    pdf.s3_file_name = "pdfs/{0}".format(pdf.hj_filename)
                else:
                    print('{0} This file is already in our database, but not on s3'.format(pdf.hj_filename))
                    print('Uploading to s3')
                    p = Release.objects.get(hj_url = pdf.s3_file_name)
            p.upload_to_s3(pdf.downloaded_file, pdf.hj_filename)
            length = p.check_pdf_length(pdf.downloaded_file, pdf.hj_filename)
            p.release_name_parser(pdf.s3_file_name, length)
            njsp = Agency.objects.get(ori7="NJNSP00")
            p.data_source = njsp
            p.save()
    else:
        print('No new files at this time. Try again later.')

def command_line_main():
    '''
    Collect the command line arguments and run the scrapers.
    This just downloads the files locally
    '''
    parser = argparse.ArgumentParser(description="Scrape and download crime data from NJSP at http://www.njsp.org/ucr/current-crime-data1.shtml?agree=0")
    parser.add_argument('-u', dest='url', help='Pass in a different URL to scrape from the standard pattern.')
    parser.add_argument('-d', dest='date', help='Perhaps you want a previous date?')

    args = parser.parse_args()

    if args.date:
        conf = CrimeUpdate(scrape_date=args.date)
    else:
        conf = CrimeUpdate()

    if args.url:
        conf.update_url(args.url)
    else:
        print("Using the standard URL")
    print("Requesting {0}".format(conf.url))
    conf.scrape()
    new_files = conf.download()

if __name__ == '__main__':
    command_line_main()