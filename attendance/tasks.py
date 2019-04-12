import logging

from attendance.helpers.async_exporter_helpers import \
    AttendanceServiceAsyncExporter
from attendance.models import AttendanceService
from attendance.views.export import export_attendance
from gatheros_subscription.celery import app

logger = logging.getLogger(__name__)


@app.task(bind=True, ignore_result=True)
def async_attendance_exporter_task(service_pk: int) -> None:
    service = AttendanceService.objects.get(pk=service_pk)

    exporter = AttendanceServiceAsyncExporter(service)

    assert exporter.has_export_lock(), \
        "Attempting to export with no lock file on event id: {}, " \
        "attendance id: {}".format(
            service.event.pk,
            service.pk,
        )

    payload = export_attendance(service)
    if exporter.has_existing_export_files():
        exporter.remove_export_files()

    exporter.create_export_file(payload)

    exporter.remove_export_lock()
