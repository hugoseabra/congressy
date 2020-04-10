from celery import Celery
from kombu import Queue, Exchange

from project.system import get_system_alias

system_alias = get_system_alias()

app = Celery(system_alias)
app.config_from_object('django.conf:settings', namespace='CELERY')

app_names = (
    'attendance',
    'buzzlead',
    'gatheros_subscription',
    'mailer',
    'cgsy_video',
)

queues = list()

for app_name in app_names:
    queues.append(Queue(
        name=app_name,
        exchange=Exchange(name=system_alias, type='direct', delivery_mode=2),
        routing_key=app_name,
        durable=True,
    ))

app.conf.task_queues = queues

app.autodiscover_tasks()
