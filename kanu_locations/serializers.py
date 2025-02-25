from rest_framework import serializers

from .models import *


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ('id', 'name', 'name_ascii', 'uf')
