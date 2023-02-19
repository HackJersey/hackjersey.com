#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
from datetime import date, datetime, timedelta

import urlparse
import os

import requests
import boto3

class file:
    def __init__(self, url):
        self.url = url

    def download(self):
        r = requests.get(self.url)
        self.contents = r.content
        self.filename = urlparse.urlsplit(r.url).path.split('/')[-1]
        return 

    def upload_to_s3(self, bucket=None):
        self.path = "pdfs/"+self.filename
        if not bucket:
           bucket = "njsp-crime-reports"
        conn = S3Connection(AWS_ACCESS_KEY, AWS_SECRET_KEY, host = 's3-us-east-1.amazonaws.com')
        key = conn.get_bucket(bucket).get_key(path)
        if not key:
            key = Key(conn.get_bucket(bucket))
            key.key = path
        key.set_contents_from_string(self.contents)
        key.set_acl('public-read')
        conn.close()
        return 

'''
Do this in boto3
having some issue with perms in AWS IAM
s3 = boto3.resource('s3', aws_access_key_id="", aws_secret_access_key="")
s3.Object('njsp-crime-reports', 'pdfs/2006-bias.pdf').put(Body="hiya", ACL="public-read")
'''




def main():
    '''
    Collect the command line arguments and run the scrapers.
    '''
    parser = argparse.ArgumentParser(description="Scrape IRE/NICAR schedules into CSVs")
    parser.add_argument('conf', default='NICAR', nargs='?', help='What conference do you want a schedule for? IRE or NICAR?')
    parser.add_argument('-g', dest='gcal', action='store_true', help='Create a CSV in a Gcal-friendly format.')
    parser.add_argument('-u', dest='url', help='Pass in a different URL to scrape from the standard pattern.')
    parser.add_argument('-y', dest='year', help='Perhaps you want a previous year?')


if __name__ == '__main__':
    pass
