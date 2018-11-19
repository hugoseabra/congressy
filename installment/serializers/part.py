from rest_framework import serializers

from core.serializers import FormSerializerMixin
from installment.models import Part
from installment.services import PartService


class PartSerializer(FormSerializerMixin,
                     serializers.ModelSerializer):
    class Meta:
        form = PartService
        model = Part
        fields = '__all__'
