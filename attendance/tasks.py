import logging

from attendance.helpers.async_exporter_helpers import \
    AttendanceServiceAsyncExporter
from attendance.models import AttendanceService
from attendance.views.export import export_attendance
from gatheros_subscription.celery import app

logger = logging.getLogger(__name__)


@app.task(bind=True,
          rate_limit='5/m',  # Processar até 10 tasks por minuto
          default_retry_delay=30,  # retry in 30s
          ignore_result=True)
def async_attendance_exporter_task(*args, **kwargs):
    try:
        event_pk = kwargs.get('event_pk')
        service_pk = kwargs.get('service_pk')
        service = AttendanceService.objects.get(pk=service_pk,
                                                event_id=event_pk)

        exporter = AttendanceServiceAsyncExporter(service)

        if exporter.has_export_lock():
            raise Exception('Exportação já está em andamento por outro usuário.')

        exporter.create_export_lock()

        payload = export_attendance(service)
        if exporter.has_existing_export_files():
            exporter.remove_export_files()

        exporter.create_export_file(payload)

        exporter.remove_export_lock()
    except Exception as e:
        raise self.retry(exec=e)
