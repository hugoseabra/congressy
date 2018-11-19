from rest_framework import serializers

from core.serializers import FormSerializerMixin
from installment.models import Contract
from installment.services import ContractService


class ContractSerializer(FormSerializerMixin,
                         serializers.ModelSerializer):
    limit_date = serializers.DateField(input_formats=[
        '%d/%m/%Y',
    ])

    class Meta:
        form = ContractService
        model = Contract
        fields = '__all__'
        read_only_fields = ('status', 'minimum_amount_creation')
