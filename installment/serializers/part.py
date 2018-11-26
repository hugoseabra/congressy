from rest_framework import serializers

from core.serializers import FormSerializerMixin
from installment.models import Part
from installment.services import PartService


class PartSerializer(FormSerializerMixin,
                     serializers.ModelSerializer):
    
    expiration_date = serializers.DateField(input_formats=[
        '%d/%m/%Y',
        '%Y-%m-%d',
    ])

    class Meta:
        form = PartService
        model = Part
        # noinspection PyProtectedMember
        exclude = PartService.manager_class.Meta.exclude
