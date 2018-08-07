#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
from datetime import date, datetime, timedelta

import requests
from lxml import html
import unicodecsv

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
        self.new_files = []

    def add(self, file):
        '''
        Add a new file url to the update list.
        '''
        self.new_files.append(file)

    def update_url(self, url):
        '''
        Update the URL if a user passes in a command-line argument specifying a non-default URL.
        '''
        self.url = url

    def scrape(self):
        '''
        Scrape each the page to get the urls of the items we need to download
        '''
        r = requests.get(self.url)
        if not r.ok:
            print "Invalid URL. Please specify a valid URL to scrape with the -u flag."
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
                    self.add(link)
                else:
                    print('skipping {0}'.format(link))

    def download(self):
        for pdf in self.new_files:
            r = requests.get(pdf)
            local_name = 'downloads/{0}'.format(pdf.split('/')[-1])
            with open(local_name, 'wb') as f:
                f.write(r.content)
            print('Downloaded {0}'.format(local_name))

        print('Downloaded {0} files from NJSP.').format(len(self.new_files))
        return


def main():
    '''
    Collect the command line arguments and run the scrapers.
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
    print "Requesting {0}".format(conf.url)
    conf.scrape()
    conf.download()


if __name__ == '__main__':
    main()


#TODO upload the results to AWS and give me back the published URLS
#TODO finally, append those new URLs to the csv

#then make a database for all of those with either django or flask
