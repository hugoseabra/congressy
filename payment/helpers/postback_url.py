import os
import tempfile

import absoluteuri
from django.conf import settings
from django.urls import reverse
from core.helpers import sentry


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


def get_ngrok_host():
    """
    NGROK é um serviço utilizado para criar um host público em qualquer
    ambiente fazendo um túnel de portas.

    O serviço é ativado no container específco para isso em
    bin/env/docker-compose_dev.yml no qual ele escreve o endereço gerado no
    ngrok em um arquivo e é compartilhado pelo host.
    """
    ngrok_file = os.path.join(tempfile.gettempdir(), 'ngrok', 'ngrok.txt')

    if os.path.isfile(ngrok_file) is False:
        sentry.log('Ngrok host was not found.', type='warning')
        return None

    with open(ngrok_file) as f:
        host = f.read()
        f.close()

        if not host:
            sentry.log(
                'Ngrok host was not found in existing file.',
                type='warning'
            )
            return None

        return host
