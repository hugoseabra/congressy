import locale
from decimal import Decimal

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
    free_interests_parts = serializers.ListField(
        required=False,
    )

    def to_representation(self, data):
        rep = super().to_representation(data)

        amount = Decimal(rep['amount'])
        installment_amount = Decimal(rep['installment_amount'])
        interests_amount = Decimal(rep['interests_amount'])
        interests_rate_percent = Decimal(rep['interests_rate_percent'])

        rep.update({
            'amount': round(amount, 2),
            'installment_amount': round(installment_amount, 2),
            'interests_amount': round(Decimal(interests_amount), 2),
            'interests_rate_percent':
                round(Decimal(interests_rate_percent), 2),
        })

        rep['installment_amount_display'] = installment_amount

        part = int(rep['installment'])

        locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

        if part in rep.get('free_interests_parts', None):
            rep['installment_amount_display'] = '{} {}'.format(
                locale.currency(
                    installment_amount,
                    grouping=True,
                    symbol=None,
                ),
                round(installment_amount, 2),
                '(sem juros)',
            )

        return rep
