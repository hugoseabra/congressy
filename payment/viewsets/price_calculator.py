from decimal import Decimal

from django.conf import settings
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from payment.installments import Calculator
from payment.serializers import (
    PriceCalculatorSerializer,
)


@api_view(['GET'])
@permission_classes((AllowAny,))
def get_installment_prices(request, amount=None):
    if not amount:
        content = {'detail': ['You must provide a price.']}
        return Response(data=content, status=status.HTTP_400_BAD_REQUEST)

    amount = Decimal(amount)

    interests_rate = settings.CONGRESSY_INSTALLMENT_INTERESTS_RATE
    min_installment_price = settings.CONGRESSY_MINIMUM_AMOUNT_FOR_INSTALLMENTS
    calculator = Calculator(
        interests_rate=Decimal(interests_rate / 100),
        total_installments=10,
    )

    prices = list()
    total_prices = list()
    for price in calculator.get_installment_prices(amount):
        if price < min_installment_price:
            continue
        prices.append(price)

    for price in calculator.get_installment_totals(amount):

        total_prices.append(price)

    response_data = list()
    for i in range(0, len(prices)):
        serializer = PriceCalculatorSerializer(
            context={
                'request': request,
            },
            data={
                'installment': i + 1,
                'installment_amount': round(prices[i], 2),
                'amount': round(total_prices[i], 2),
            }
        )
        serializer.is_valid(raise_exception=True)

        response_data.append(serializer.data)

    return Response(data=response_data)
