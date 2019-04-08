from rest_framework import serializers

from gatheros_event.serializers import PersonSerializer, EventSerializer
from gatheros_subscription.models import Subscription
from .fields import CheckinsField, AttendedStatusField
from .lot import LotSerializer

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

        if kwargs['context']['request']:
            fields = kwargs['context']['request'].query_params.get('fields')
        else:
            fields = None

        if fields:
            fields = fields.split(',')
            # Drop any fields that are not specified in the `fields` argument.
            allowed = set(fields)
            existing = set(self.fields.keys())
            # @TODO - dar suporte a filtro de campos de objetos relacionados.
            for field_name in existing - allowed:
                self.fields.pop(field_name)


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
