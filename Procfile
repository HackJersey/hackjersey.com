web: newrelic-admin run-program gunicorn project.wsgi -b 0.0.0.0:\$PORT -w 3 -k gevent --max-requests 250 --log-file - -t 25
worker: celery worker --app project --beat --loglevel info