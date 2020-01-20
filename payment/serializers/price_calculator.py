from rest_framework import serializers


class PriceCalculatorSerializer(serializers.Serializer):
    amount = serializers.DecimalField(
        decimal_places=2,
        max_digits=11,
        required=True,
    )
    installment_amount = serializers.DecimalField(
        decimal_places=2,
        max_digits=11,
        required=True,
    )
    installment = serializers.IntegerField(
        min_value=1,
        required=True,
    )
