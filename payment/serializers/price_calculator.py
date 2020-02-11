import locale
from decimal import Decimal

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
    no_interests_installments = serializers.ListField(
        required=False,
    )

    def to_representation(self, data):
        rep = super().to_representation(data)

        rep['installment_amount_display'] = rep['installment_amount']

        part = int(rep['installment'])

        locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

        if part in rep.get('no_interests_installments', None):
            rep['installment_amount_display'] = '{} {}'.format(
                locale.currency(
                    Decimal(rep['installment_amount']),
                    grouping=True,
                    symbol=None,
                ),
                '(sem juros)',
            )

        del rep['no_interests_installments']

        return rep
