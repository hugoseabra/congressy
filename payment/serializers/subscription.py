from rest_framework import serializers

from gatheros_subscription.models import Subscription


class SubscriptionSerializer(serializers.ModelSerializer):
    person = serializers.CharField(source='person.name')
    event = serializers.CharField(source='event.name')

    class Meta:
        model = Subscription
        fields = [
            'event',
            'person',
        ]
