import json

from django.conf import settings
from django.http import Http404
from rest_framework.decorators import api_view
from rest_framework.response import Response

from mailer.tasks import send_mail
from payment.models import Transaction, TransactionStatus


@api_view(['POST'])
def postback_url_view(request, uidb64):

    body = """
            We have received a postback call, here is the data:
            
            <pre><code>{0}</code></pre>
    """.format(json.dumps(request.data))

    send_mail(subject="Recived a postbackcall", body=body, to=settings.ALERT_EMAILS)

    if not uidb64:
        raise Http404
    try:
        transaction = Transaction.objects.get(uuid=uidb64)

        data = request.data
        transaction_status = TransactionStatus(
            transaction=transaction,
            data=data
        )

        transaction.data['status'] = data['current_status']
        transaction.save()

        transaction_status.save()

    except Transaction.DoesNotExist:
        raise Http404

    return Response(status=201)

