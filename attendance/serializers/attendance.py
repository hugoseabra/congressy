from rest_framework import serializers

from attendance import models

REST_FRAMEWORK = {
    'DATETIME_FORMAT': "%Y-%m-%d %H:%M:%S",
}


class AttendanceServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.AttendanceService
        fields = '__all__'
