from .base import DataCleanerBase, FilterMixin


class AttendanceDataCleaner(DataCleanerBase, FilterMixin):
    filter_dict = (
        ('attendance.AttendanceService', 'event_id',),
        ('attendance.AttendanceCategoryFilter', 'attendance_service__event_id',),
        ('attendance.Checkin', 'attendance_service__event_id',),
        ('attendance.Checkout', 'checkin__attendance_service__event_id',),
    )
