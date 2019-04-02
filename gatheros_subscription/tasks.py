import logging

from gatheros_event.models import Event
from gatheros_subscription.celery import app
from gatheros_subscription.helpers.async_exporter_helpers import (
    has_export_lock,
    remove_export_lock,
    has_existing_export_files,
    create_export_file,
    remove_export_files,
)
from gatheros_subscription.helpers.export import export_event_data

logger = logging.getLogger(__name__)


@app.task(ignore_result=True)
def async_exporter(event_pk: int) -> None:
    event = Event.objects.get(pk=event_pk)

    assert has_export_lock(event), \
        "Attempting to export with no lock file on event id: {}".format(
            event.pk
        )

    payload = export_event_data(event)
    if has_existing_export_files(event):
        remove_export_files(event)

    create_export_file(event, payload)

    remove_export_lock(event)
