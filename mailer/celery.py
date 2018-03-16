import logging
import os

from celery import Celery

logger = logging.getLogger("Celery[Mailer]")

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings.prod')

app = Celery('mailer')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
