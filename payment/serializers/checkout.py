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
            'transaction_type': data.get('transaction_type'),
            'installments': data.get('installments'),
            'installment_part': data.get('installment_part'),
            'amount': data.get('amount'),
            'card_hash': data.get('card_hash'),
            'subscription': data.get('subscription'),
            'selected_lot': data.get('selected_lot'),
            'benefactor': data.get('benefactor'),
        }

    def update(self, instance, validated_data):
        raise NotImplementedError

    def create(self, validated_data):
        raise NotImplementedError

    def get_transaction_id(self, obj):
        pass
