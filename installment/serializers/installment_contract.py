from rest_framework import serializers

from core.serializers import FormSerializerMixin
from installment.models import InstallmentContract
from installment.services import InstallmentContractService


class InstallmentContractSerializer(FormSerializerMixin,
                                    serializers.ModelSerializer):
    class Meta:
        form = InstallmentContractService
        model = InstallmentContract
        fields = '__all__'
