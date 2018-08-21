import base64
import binascii
from uuid import uuid4
from django.core.files.base import ContentFile
from rest_framework import serializers

from addon import models
from gatheros_subscription.models import LotCategory


class LotCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = LotCategory
        fields = (
            'id',
            'name',
        )


class ThemeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Theme
        fields = '__all__'


class OptionalProductTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.OptionalProductType
        fields = '__all__'


class OptionalServiceTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.OptionalServiceType
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Product
        fields = '__all__'

    def __init__(self, *args, **kwargs):

        data = kwargs.get('data')

        if data:
            possible_base64 = data.get('banner')
            if possible_base64:
                # Decoding from base64 avatar into a file obj.
                try:
                    file_ext, imgstr = possible_base64.split(';base64,')
                    ext = file_ext.split('/')[-1]
                    file_name = str(uuid4()) + "." + ext
                    data._mutable = True
                    data['banner'] = ContentFile(
                        base64.b64decode(imgstr),
                        name=file_name
                    )
                    data._mutable = False
                    kwargs.update({'data': data})
                except (binascii.Error, ValueError):
                    pass

        super().__init__(*args, **kwargs)


class SubscriptionProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.SubscriptionProduct
        fields = '__all__'


class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Service
        fields = '__all__'

    def __init__(self, *args, **kwargs):

        data = kwargs.get('data')

        if data:
            possible_base64 = data.get('banner')
            if possible_base64:
                # Decoding from base64 avatar into a file obj.
                try:
                    file_ext, imgstr = possible_base64.split(';base64,')
                    ext = file_ext.split('/')[-1]
                    file_name = str(uuid4()) + "." + ext
                    data._mutable = True
                    data['banner'] = ContentFile(
                        base64.b64decode(imgstr),
                        name=file_name
                    )
                    data._mutable = False
                    kwargs.update({'data': data})
                except (binascii.Error, ValueError):
                    pass

        super().__init__(*args, **kwargs)


class SubscriptionServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.SubscriptionService
        fields = '__all__'
