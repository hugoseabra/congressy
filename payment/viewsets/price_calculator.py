import uuid
from decimal import Decimal

from django.conf import settings
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from gatheros_subscription.models import Subscription
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

    free_installments = 0

    if 'subscription' in request.GET:
        sub_pk = request.GET.get('subscription')
        try:
            uuid.UUID(sub_pk)
        except ValueError:
            content = {'details': ['Invalid UUID for subscription']}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        try:
            sub = Subscription.objects.get(
                pk=str(sub_pk),
                test_subscription=False,
            )

            lot = sub.lot

            if lot.num_install_interest_absortion:
                free_installments = lot.num_install_interest_absortion

        except Subscription.DoesNotExist:
            content = {'details': ['Subscription not found']}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

    amount = Decimal(amount)

    interests_rate = settings.CONGRESSY_INSTALLMENT_INTERESTS_RATE
    min_installment_price = settings.CONGRESSY_MINIMUM_AMOUNT_FOR_INSTALLMENTS
    calculator = Calculator(
        interests_rate=Decimal(interests_rate / 100),
        total_installments=10,
        free_installments=free_installments,
    )

    prices = list()
    total_prices = list()
    free_interests_parts = list()
    installment_part = 1

    for price in calculator.get_installment_prices(amount):
        if price < min_installment_price:
            continue
        prices.append(price)

        if installment_part <= free_installments:
            free_interests_parts.append(installment_part)

        installment_part += 1

    for price in calculator.get_installment_totals(amount):
        total_prices.append(price)

    response_data = list()
    for i in range(0, len(prices)):
        total_amount = total_prices[i]
        interests_amount = total_amount - amount

        serializer = PriceCalculatorSerializer(
            context={
                'request': request,
            },
            data={
                'installment': i + 1,
                'free_interests_parts': free_interests_parts,
                'interests_rate_percent': interests_rate,
                'installment_amount': round(prices[i], 2),
                'interests_amount': round(interests_amount, 2),
                'amount': round(total_prices[i], 2),
            }
        )
        serializer.is_valid(raise_exception=True)

        response_data.append(serializer.data)

    return Response(data=response_data)
