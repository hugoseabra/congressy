from rest_framework import serializers

from attendance import models
from gatheros_event.serializers import PersonSerializer, EventSerializer
from gatheros_subscription.models import Subscription, Lot

REST_FRAMEWORK = {
    'DATETIME_FORMAT': "%Y-%m-%d %H:%M:%S",
}


class DynamicFieldsModelSerializer(serializers.ModelSerializer):
    """
    A ModelSerializer that takes an additional `fields` argument that
    controls which fields should be displayed.
    """

    def __init__(self, *args, **kwargs):
        # Instantiate the superclass normally
        super(DynamicFieldsModelSerializer, self).__init__(*args, **kwargs)

        fields = kwargs['context']['request'].query_params.get('fields')
        if fields:
            fields = fields.split(',')
            # Drop any fields that are not specified in the `fields` argument.
            allowed = set(fields)
            existing = set(self.fields.keys())
            # @TODO - dar suporte a filtro de campos de objetos relacionados.
            for field_name in existing - allowed:
                self.fields.pop(field_name)


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

        service_pk = self.context.get('attendance_service_pk')
        if not service_pk:
            raise Exception(
                'You must provide "attendance_service_pk" in Serializer'
                ' context.'
            )

        subs_checkins = obj.filter(attendance_service__pk=service_pk)
        subs_checkins = subs_checkins.order_by(
            'created_on',
            'attendance_service__name'
        )

        for checkin in subs_checkins:

            service = checkin.attendance_service

            try:
                checkout = checkin.checkout
                checkout = {
                    'id': checkout.pk,
                    'created_by': checkout.created_by,
                    'created_on': checkin.created_on.strftime(
                        '%d/%m/%Y %H:%M:%S'
                    ),
                }
            except AttributeError:
                checkout = None

            checkins.append({
                'id': checkin.pk,
                'attendance_name': service.name,
                'attendance_pk': service.pk,
                'created_by': checkin.created_by,
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
    def to_internal_value(self, data):
        pass

    def to_representation(self, obj):
        service_pk = self.context.get('attendance_service_pk')
        if not service_pk:
            raise Exception(
                'You must provide "attendance_service_pk" in Serializer'
                ' context.'
            )

        checkin = obj.checkins.filter(attendance_service__pk=service_pk)

        if checkin.count() == 0:
            return False

        checkin = checkin.last()

        return not hasattr(checkin, 'checkout')


class SubscriptionAttendanceSerializer(DynamicFieldsModelSerializer):
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

    def validate_subscription(self, value):
        if value.confirmed is False:
            raise serializers.ValidationError(
                'Esta inscrição não está confirmada.'
            )

        return value

    def validate(self, attrs):
        subscription = attrs.get('subscription')
        service = attrs.get('attendance_service')
        checkins = subscription.checkins.filter(attendance_service=service)
        if checkins.count() and not hasattr(checkins.last(), 'checkout'):
            raise serializers.ValidationError({
                'subscription': 'Entrada já registrada neste Atendimento para'
                                ' esta inscrição.'
            })

        return attrs


class CheckoutSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Checkout
        fields = '__all__'

    def validate_checkin(self, value):
        if hasattr(value, 'checkout') and value.checkout.pk:
            raise serializers.ValidationError(
                'Saída já registrada.'
            )

        return value
