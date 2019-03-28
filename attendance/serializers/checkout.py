from rest_framework import serializers

from attendance import models

REST_FRAMEWORK = {
    'DATETIME_FORMAT': "%Y-%m-%d %H:%M:%S",
}


class CheckoutSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Checkout
        fields = '__all__'

    def validate_checkin(self, value):
        if hasattr(value, 'checkout') and value.checkout.pk:
            raise serializers.ValidationError(
                'Saída já registrada.'
            )

        return value
