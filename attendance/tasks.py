import logging

from attendance.helpers.async_exporter_helpers import \
    AttendanceServiceAsyncExporter
from attendance.models import AttendanceService
from attendance.views.export import export_attendance
from gatheros_subscription.celery import app

logger = logging.getLogger(__name__)


@app.task(bind=True,
          rate_limit='10/m',  # Processar até 10 tasks por minuto
          default_retry_delay=2 * 60,  # retry in 2m
          ignore_result=True)
def async_attendance_exporter_task(self, event_pk: int, service_pk: int):
    service = AttendanceService.objects.get(pk=service_pk,
                                            event_id=event_pk)

    exporter = AttendanceServiceAsyncExporter(service)

    try:
        if exporter.has_export_lock():
            raise Exception(
                'Exportação já está em andamento por outro usuário.'
            )

        exporter.create_export_lock()

        payload = export_attendance(service)
        if exporter.has_existing_export_files():
            exporter.remove_export_files()

        exporter.create_export_file(payload)

        exporter.remove_export_lock()
    except Exception as exc:
        raise self.retry(exc=exc)
