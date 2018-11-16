from rest_framework import serializers

from core.serializers import FormSerializerMixin
from installment.models import InstallmentPart
from installment.services import InstallmentPartService


class InstallmentPartSerializer(FormSerializerMixin,
                                serializers.ModelSerializer):
    class Meta:
        form = InstallmentPartService
        model = InstallmentPart
        fields = '__all__'
