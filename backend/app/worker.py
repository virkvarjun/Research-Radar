"""RQ worker entry point."""

import redis
from rq import Worker, Queue

from app.config import settings

conn = redis.from_url(settings.redis_url)

if __name__ == "__main__":
    queues = [Queue("default", connection=conn), Queue("ingest", connection=conn)]
    worker = Worker(queues, connection=conn)
    worker.work()
