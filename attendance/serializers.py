from rest_framework import serializers

from attendance import models
from gatheros_event.serializers import PersonSerializer, EventSerializer
from gatheros_subscription.models import Subscription, Lot

REST_FRAMEWORK = {
    'DATETIME_FORMAT': "%Y-%m-%d %H:%M:%S",
}


class AttendanceServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.AttendanceService
        fields = '__all__'


class LotSerializer(serializers.ModelSerializer):
    category = serializers.StringRelatedField()

    class Meta:
        model = Lot
        fields = (
            'id',
            'name',
            'price',
            'limit',
            'private',
            'category',
            'date_start',
            'date_end',
        )


class CheckinsField(serializers.Field):
    def to_representation(self, obj):
        checkins = []
        for checkin in obj.all():

            try:
                checkout = checkin.checkout
                checkout = {
                    'attended_by': checkout.attended_by,
                    'created_on': checkin.created_on.strftime(
                        '%d/%m/%Y %H:%M:%S'
                    ),
                }
            except AttributeError:
                checkout = None

            checkins.append({
                'attended_by': checkin.attended_by,
                'attendance_service': checkin.attendance_service.name,
                'printed_on': checkin.printed_on.strftime(
                    '%d/%m/%Y %H:%M:%S'
                ) if checkin.printed_on else None,
                'created_on': checkin.created_on.strftime(
                    '%d/%m/%Y %H:%M:%S'
                ),
                'checkout': checkout
            })

        return checkins


class AttendedStatusField(serializers.Field):
    def to_representation(self, obj):
        checkin = obj.checkins.last()

        if not checkin:
            return False

        try:
            checkin.checkout
            return False

        except AttributeError:
            return True


class SubscriptionAttendanceSerializer(serializers.ModelSerializer):
    event = EventSerializer()
    lot = LotSerializer()
    person = PersonSerializer()
    checkins = CheckinsField()
    attendance_status = AttendedStatusField(source='*')

    class Meta:
        model = Subscription
        fields = (
            'uuid',
            'status',
            'code',
            'event_count',
            'created',
            'modified',
            'event',
            'lot',
            'person',
            'checkins',
            'attendance_status',
        )


class CheckinSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Checkin
        fields = '__all__'


class CheckoutSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Checkin
        fields = '__all__'
