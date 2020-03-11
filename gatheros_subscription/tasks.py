import logging

from gatheros_event.models import Event
from gatheros_subscription.helpers.export import export_event_data
from gatheros_subscription.helpers.subscription_async_exporter import \
    SubscriptionServiceAsyncExporter
from project.celery import app

logger = logging.getLogger(__name__)


@app.task(bind=True,
          queue='gatheros_subscription',
          options={'queue': 'gatheros_subscription'},
          rate_limit='5/m',  # Processar até 5 tasks por minuto
          default_retry_delay=30,  # retry in 30s
          ignore_result=True)
def async_subscription_exporter_task(self, event_pk: int) -> None:
    event = Event.objects.get(pk=event_pk)

    exporter = SubscriptionServiceAsyncExporter(event)

    try:

        if not exporter.has_export_lock():
            logger.warning(
                "Creating missing exporter lock for event id: {}".format(
                    event.pk
                ))
            exporter.create_export_lock()

        payload = export_event_data(event)
        if exporter.has_existing_export_files():
            exporter.remove_export_files()

        exporter.create_export_file(payload)

        exporter.remove_export_lock()
    except Exception as e:
        exporter.remove_export_lock()
        raise self.retry(exec=e)
