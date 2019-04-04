import logging
import os

from celery import Celery

logger = logging.getLogger("Celery[SubscriptionExporter]")

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.manage.settings.dev')

app = Celery('subscription_exporter')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

