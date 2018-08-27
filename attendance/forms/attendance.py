from django import forms
from attendance.models.attendance import Attendance


class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = (
            'attended_by',
            'subscription',
            'attendance_service',
        )
