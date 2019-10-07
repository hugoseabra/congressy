from rest_framework import serializers

from core.serializers import FormSerializerMixin
from payment.pagarme.forms import SubscriptionCheckoutForm


class SubscriptionCheckoutSerializer(FormSerializerMixin,
                                     serializers.Serializer):
    transaction_id = serializers.SerializerMethodField()

    class Meta:
        form = SubscriptionCheckoutForm

    def to_internal_value(self, data):
        return {
            'event_pk': data.get('event'),
            'transaction_type': data.get('transaction_type'),
            'num_installments': data.get('num_installments'),
            'installment_part_pk': data.get('installment_part'),
            'interests_amount': data.get('interests_amount'),
            'boleto_expiration_date': data.get('boleto_expiration_date'),
            'card_hash': data.get('card_hash'),
            'subscription_pk': data.get('subscription'),
            'benefactor_pk': data.get('benefactor'),
        }

    def update(self, instance, validated_data):
        raise NotImplementedError

    def create(self, validated_data):
        raise NotImplementedError

    def get_transaction_id(self, obj):
        pass
