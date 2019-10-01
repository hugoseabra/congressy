from rest_framework import serializers

from payment.models import TransactionStatus


class TransactionStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransactionStatus
        exclude = ('data', 'transaction',)
        read_only_fields = [
            f.name
            for f in TransactionStatus._meta.get_fields()
        ]
