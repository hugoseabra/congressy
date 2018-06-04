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


class SubscriptionProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.SubscriptionProduct
        fields = '__all__'


class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Service
        fields = '__all__'


class SubscriptionServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.SubscriptionService
        fields = '__all__'
