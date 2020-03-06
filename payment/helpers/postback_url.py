import absoluteuri
from django.conf import settings
from django.urls import reverse

from project.system import get_ngrok_host


def get_postback_url(transaction_id):
    if settings.DEBUG is True:
        ngrok_host = get_ngrok_host()

        if ngrok_host:
            url = reverse(
                'api:payment:payment_postback_url',
                kwargs={'uidb64': transaction_id}
            )

            return '{host}{url}'.format(host=ngrok_host, url=url)

    return absoluteuri.reverse(
        'api:payment:payment_postback_url',
        kwargs={'uidb64': transaction_id}
    )
