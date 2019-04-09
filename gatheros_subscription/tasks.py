import logging

from gatheros_event.models import Event
from gatheros_subscription.celery import app
from gatheros_subscription.helpers.export import export_event_data
from gatheros_subscription.helpers.subscription_async_exporter import \
    SubscriptionServiceAsyncExporter

logger = logging.getLogger(__name__)


@app.task(ignore_result=True)
def async_subscription_exporter_task(event_pk: int) -> None:
    event = Event.objects.get(pk=event_pk)

    exporter = SubscriptionServiceAsyncExporter(event)

    assert exporter.has_export_lock(), \
        "Attempting to export with no lock file on event id: {}".format(
            event.pk
        )

    payload = export_event_data(event)
    if exporter.has_existing_export_files():
        exporter.remove_export_files()

    exporter.create_export_file(payload)

    exporter.remove_export_lock()
