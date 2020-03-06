import os
import tempfile

import absoluteuri
from django.conf import settings

from core.helpers import sentry


def get_system_name():
    return os.getenv('CGSY_SYSTEM_NAME') or 'Congressy'


def get_system_alias():
    return os.getenv('CGSY_SYSTEM_ALIAS') or 'congressy'


def get_system_owner_link():
    return os.getenv('CGSY_SYSTEM_OWNER_LINK') or 'https://congressy.com'


def get_system_owner_terms_link():
    link = os.getenv('CGSY_SYSTEM_TERMS_LINK')
    return link or 'https://www.congressy.com/termos-de-uso/'


def get_system_main_logo():
    path = 'assets/img/logos/{}'.format(get_system_alias())
    path += '/cgsy_system_main_logo.png'
    return settings.STATIC_URL + path


def get_system_voucher_logo():
    path = 'assets/img/logos/{}'.format(get_system_alias())
    path += '/cgsy_system_voucher_logo.png'
    return settings.STATIC_URL + path


def get_system_registration_logo():
    path = 'assets/img/logos/{}'.format(get_system_alias())
    path += '/cgsy_system_registration_logo.png'
    return settings.STATIC_URL + path


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


def get_system_url(path: str = None):
    if settings.DEBUG is True:
        url = get_ngrok_host()
    else:
        url = absoluteuri.build_absolute_uri('')

    if url.endswith('/') is False:
        url += '/'

    if path:
        if str(path).startswith('/') is True:
            path = path.lstrip('/')

        if str(path).endswith('/') is False:
            path += '/'

        url += path

    return url
