import logging
import os

from celery import Celery

logger = logging.getLogger("Celery[Exporter]")

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.manage.settings.prod')

app = Celery('exporter')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

