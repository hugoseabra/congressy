""" django app """
# pylint: disable=C0111,W0612
from django.apps import AppConfig


class AttendanceConfig(AppConfig):
    name = 'attendance'
    verbose_name = 'Atendimentos'

    # noinspection PyUnresolvedReferences
    def ready(self):
        import attendance.signals
