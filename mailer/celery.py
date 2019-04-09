import logging
import os

from celery import Celery
from kombu import Queue, Exchange

logger = logging.getLogger("Celery[Mailer]")

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.manage.settings.dev')

CELERY_QUEUES = (
    Queue(
        'celery',
        Exchange('transient', delivery_mode=2),
        routing_key='celery',
        durable=True,
    ),
)

app = Celery('mailer')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
