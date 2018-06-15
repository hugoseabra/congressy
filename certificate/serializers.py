from rest_framework import serializers
from drf_extra_fields.fields import Base64ImageField
from certificate.models import Certificate


class CertificateSerializer(serializers.ModelSerializer):
    background_image = Base64ImageField()

    class Meta:
        model = Certificate
        fields = '__all__'

