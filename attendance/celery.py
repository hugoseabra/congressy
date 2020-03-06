import logging
import os

from celery import Celery
from kombu import Queue, Exchange

from project.system import get_system_alias
from django.apps import apps

dir_name = os.path.basename(os.path.dirname(__file__))

system_alias = get_system_alias()
namespace = 'CELERY_{}'.format(system_alias.upper())

app = apps.get_app_config(app_label=dir_name)
queue_name = app.name

CELERY_QUEUES = (
    Queue(
        name=system_alias,
        exchange=Exchange(name='transient', type='direct', delivery_mode=2),
        routing_key='{}.{}'.format(system_alias, queue_name),
        durable=True,
    ),
)

logger = logging.getLogger("Celery[{}]".format(queue_name.title()))

app = Celery(queue_name)
app.config_from_object('django.conf:settings', namespace=namespace)
app.autodiscover_tasks()
