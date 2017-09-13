import os

import redis
from rq import Worker, Queue, Connection
from django.conf import settings

listen = ['high', 'default', 'low']

redis_url = os.getenv('REDISTOGO_URL', 'redis://redistogo:f5acd0aff98e5377361eb9136497a053@tarpon.redistogo.com:10145')

conn = redis.from_url(redis_url)

if __name__ == '__main__':
    settings.configure()
    with Connection(conn):
        worker = Worker(map(Queue, listen))
        worker.work()
