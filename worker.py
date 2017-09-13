import os

import redis
from rq import Worker, Queue, Connection
import django
from django.conf import settings
from django.core.wsgi import get_wsgi_application
listen = ['high', 'default', 'low']

redis_url = os.getenv('REDISTOGO_URL', 'redis://redistogo:f5acd0aff98e5377361eb9136497a053@tarpon.redistogo.com:10145')

conn = redis.from_url(redis_url)

if __name__ == '__main__':
    os.environ["DJANGO_SETTINGS_MODULE"] = "gettingstarted.settings"
    application = get_wsgi_application()
    with Connection(conn):
        worker = Worker(map(Queue, listen))
        worker.work()
