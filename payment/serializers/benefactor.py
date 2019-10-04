from rest_framework import serializers

from core.serializers import FormSerializerMixin
from payment.managers import BenefactorManager
from payment.models import Benefactor


class BenefactorSerializer(FormSerializerMixin, serializers.ModelSerializer):
    class Meta:
        form = BenefactorManager
        model = Benefactor
        fields = '__all__'
