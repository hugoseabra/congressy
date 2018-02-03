from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.http import Http404
from payment.models import Transaction, TransactionStatus
from rest_framework import status


@api_view(['POST'])
def postback_url_view(request, uidb64):
    if not uidb64:
        raise Http404
    try:
        transaction = Transaction.objects.get(uuid=uidb64)

        data = request.data

        transaction_status = TransactionStatus(
            transaction=transaction,
            data=data
        )

        transaction_status.save()
        print(data)

    except Transaction.DoesNotExist:
        print('dsadasdas')
        raise Http404

    return Response(status=201)

