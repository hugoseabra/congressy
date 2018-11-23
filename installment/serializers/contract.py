from rest_framework import serializers

from core.serializers import FormSerializerMixin
from installment.models import Contract
from installment.services import ContractService


class ContractSerializer(FormSerializerMixin,
                         serializers.ModelSerializer):

    class Meta:
        form = ContractService
        model = Contract
        # noinspection PyProtectedMember
        exclude = ContractService().manager._meta.exclude
        read_only_fields = ('status',)

