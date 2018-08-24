import calendar, time
from difflib import context_diff
from urllib.parse import *

from django.utils import timezone
from django.conf import settings
from django.core.mail import send_mail
import requests
from lxml import html

from project.apps.crime.models import Scraped, ScrapeSite


class PageToScrape:
    def __init__(self):
        self.urls = ScrapeSite.objects.all()

class Scraping:
    def __init__(self, ScrapeSite):
        if not ScrapeSite.url:
            self.url = "https://www.njsp.org/ucr/current-crime-data1.shtml?agree=0"
        else:
            self.url = ScrapeSite.url
        self.source_site = ScrapeSite

    def scrape(self):
        last_update = Scraped.objects.filter(source_url = self.source_site).order_by('-scraped_date').first()
        now = timezone.now()
        print('Requesting {0}'.format(self.url))
        r = requests.get(self.url, verify=False)
        admin_addresses = []
        for address in settings.ADMINS:
            admin_addresses.append(address[1])
        if not last_update:
            last_good_update = None
        else:
            last_good_update = Scraped.objects.filter(source_url = self.source_site, status_code ="200").order_by('-scraped_date').first()
        new_scraping = Scraped()
        new_scraping.status_code = r.status_code
        new_scraping.source_url = self.source_site
        if r.status_code != 200:
            print("Bad status response: {0}".format(r.status_code))
            if not last_good_update or last_update.status_code == 200:
                new_scraping.save()
                print('Saving first bad update.')
                return
            else:
                if (now - last_good_update.scraped_date) > 180:
                    email_subject = "[CRIME] {0} is broken".format(url)
                    email_body = "It has been {0} minutes since we received a valid response from {1}".format(now - last_good_update.scraped_date, url)
                    send_mail(email_subject, email_body, settings.DEFAULT_FROM_EMAIL, admin_addresses, fail_silently=False)
                    print("Sending email: {0}".format(email_body))
                    return
                else:
                    #the last update status was not "ok" but it's been less than 3 hours
                    print("The page has failed for less than 3 hours")
                    return
        #if the request is successful and the status code is 200
        else:
            #grab the hash of the new request
            tree = html.fromstring(r.content)
            #get the url and selector from the model
            my_new_table = tree.xpath(self.source_site.selector)[0].text_content()
            new_scraping.hash(my_new_table)
            my_new_lines = my_new_table.split('\r\n')
            if last_update:
                #if there is a good 200 code now
                #go forth and check the hash against last_good_update hash
                if last_good_update.html_hash and (last_good_update.html_hash != new_scraping.html_hash):
                    #pull the old html from s3
                    if last_good_update.s3_url:
                        old_r = requests.get(last_good_update.s3_url)
                        old_tree = html.fromstring(old_r.content)
                        my_old_table = old_tree.xpath(self.source_site.selector)[0].text_content()
                        my_old_lines = my_old_table.split('\r\n')
                        diff = list(context_diff(my_new_lines, my_old_lines, n=1))
                        if diff:
                            email_body = ''.join(diff).replace('\\n','\n')
                            email_body += '\nUse the fetcher.py main() function to update the database.'
                            email_subject = "[CRIME] {0} has changed!".format(self.source_site.url)
                            send_mail(email_subject, email_body, settings.DEFAULT_FROM_EMAIL, admin_addresses, fail_silently=False)
                        else:
                            print("ERROR. Hash is different but the html is not.")
                            return
                    else:
                        print("No previous successful scrape?")
                        pass
                else:
                    #the hash is not different, stop
                    print("the hash isn't different")
                    return
            else:
                email_body = "\nUse the fetcher.py main() function to update the database, if you haven't already"
                email_subject = "[CRIME] {0} is new and should be scraped!".format(self.source_site.url)
                send_mail(email_subject, email_body, settings.DEFAULT_FROM_EMAIL, admin_addresses, fail_silently=False)
            #add the datestring to the file name
            timestamp = calendar.timegm(time.gmtime())
            base_url = urlparse(self.url).path.split('/')[-1]
            url_prefix = base_url.split('.')
            new_url = "NJSP-{0}-{1}.{2}".format(url_prefix[0], timestamp, url_prefix[1])
            #upload to s3 and add the url to the model
            print("uploading the saved html to s3")
            new_scraping.upload_to_s3(r.content, new_url)
            new_scraping.save()

def main():
    new_round = PageToScrape()
    for page in new_round.urls:
        new_scrape = Scraping(page)
        new_scrape.scrape()