import logging
import os

from celery import Celery
from kombu import Queue, Exchange

CELERY_QUEUES = (
    Queue(
        'celery',
        Exchange('transient', delivery_mode=2),
        routing_key='celery',
        durable=True,
    ),
)

logger = logging.getLogger("Celery[SubscriptionExporter]")

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.manage.settings.dev')

app = Celery('subscription_exporter')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()


