from rest_framework import serializers

from core.serializers import FormSerializerMixin
from payment.managers import PayerManager
from payment.models import Payer


class PayerSerializer(FormSerializerMixin, serializers.ModelSerializer):
    class Meta:
        form = PayerManager
        model = Payer
        fields = '__all__'
