import os

from attendance.models import AttendanceService
from base.async_exporter import BaseAsyncExporter


class AttendanceServiceAsyncExporter(BaseAsyncExporter):
    exporter_url = '/attendance_exporter/'

    def __init__(self, service: AttendanceService) -> None:
        self.service = service
        super().__init__(service.event)

    def _get_exporter_folder_path(self) -> str:
        return os.path.join(
            super()._get_exporter_folder_path(),
            'attendance_services',
            '{}'.format(self.service.pk)
        )
