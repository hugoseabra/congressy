from rest_framework import serializers

from addon import models


class ThemeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Theme
        fields = '__all__'


class OptionalTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.OptionalType
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

