to start a new db, you can use 
python manage.py loaddata initial_fixture.json

or, run 
python manage.py load_initial_geodata
and
python manage.py load_initial_releases

To test subdomains, first update django-hosts and install as shown:
https://github.com/jazzband/django-hosts (this should all be handled in our code)

edit /etc/hosts/ and add names for different subdomains that alias to 127.0.0.1

in my instance, it looks like this. 
127.0.0.1	crime.localhj.app
127.0.0.1	boundary.localhj.app
127.0.0.1	www.localhj.app
127.0.0.1	localhj.app
I then add localhj.app to my number on item in my sites app

add your sites and your superuser
foreman run python manage.py shell
from django.contrib.sites.models import Site
first = Site.objects.first()
first.domain = 'localhj.app'
first.save()



then you should be good to go to hack on one of our projects

for the README, the first site in your Sites thing must be your home domain


to sync 
foreman run python manage.py dumpdata --exclude=auth --exclude=sites --exclude=crime.scraped --exclude=contenttypes > project/apps/crime/fixtures/initial_fixture.json

heroku run python manage.py createsuperuser
tommeagher
hello+crime@tommeagher.com

then herosh
from django.contrib.sites.models import Site
first = Site.objects.first()
first.domain = 'localhj.app'
first.save()

add www.hackjersey.com
crime.hackjersey.com
boundary.hackjersey.com

add superuser
add 3 sites
heroku run python manage.py loaddata initial_fixture.json

