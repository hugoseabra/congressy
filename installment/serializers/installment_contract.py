from rest_framework import serializers

from core.serializers import FormSerializerMixin
from installment.models import InstallmentContract
from installment.services import InstallmentContractService


class InstallmentContractSerializer(FormSerializerMixin,
                                    serializers.ModelSerializer):
    limit_date = serializers.DateField(input_formats=[
        '%d/%m/%Y',
    ])

    class Meta:
        form = InstallmentContractService
        model = InstallmentContract
        fields = '__all__'
        read_only_fields = ('status', 'minimum_amount_creation')
