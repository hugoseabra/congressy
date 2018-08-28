from rest_framework import serializers

from attendance import models
from gatheros_subscription.models import Subscription


class AttendanceServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.AttendanceService
        fields = '__all__'


class SubscriptionAttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = '__all__'


class CheckinSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Checkin
        fields = '__all__'


class CheckoutSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Checkin
        fields = '__all__'
