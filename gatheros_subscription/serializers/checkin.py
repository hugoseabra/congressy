from rest_framework import serializers

from gatheros_event.models import Person
from gatheros_subscription.models import Subscription


class PersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Person
        fields = (
            'name',
            'email',
            'cpf',
            'institution_cnpj',
        )


class CheckInSubscriptionSerializer(serializers.ModelSerializer):
    person = PersonSerializer()
    lot = serializers.CharField(source='lot.name')

    class Meta:
        model = Subscription
        fields = [
            'pk',
            'code',
            'person',
            'lot',
            'status',
            'event_count',
        ]
