""" Helper para inscrições. """

import base64
import json

import absoluteuri
import requests
from django.conf import settings
from django.contrib.staticfiles.storage import staticfiles_storage
from django.core.files.base import ContentFile
from django.template.loader import render_to_string


def get_logo():
    uri = staticfiles_storage.url('assets/img/logo_v3.png')
    url = settings.BASE_DIR + "/frontend" + uri
    with open(url, 'rb') as f:
        read_data = f.read()
        f.close()

    return base64.b64encode(read_data)


def get_template_path():
    return 'pdf/extract.html'


def get_context(subscription):
    """
    Resgata contexto adequado para o template de voucher
    """

    event = subscription.event
    context = {
        'base_url': absoluteuri.build_absolute_uri(settings.STATIC_URL),
        'logo': get_logo(),
        'event': event,
        'person': subscription.person,
        'lot': subscription.lot,
        'organization': event.organization,
        'subscription': subscription,
    }

    return context


def create_extract(subscription):
    wkhtml_ws_url = settings.WKHTMLTOPDF_WS_URL

    html = render_to_string(
        template_name='pdf/extract.html',
        context=get_context(subscription)
    )

    encoded = base64.b64encode(html.encode()).decode()

    data = {
        'contents': encoded,
        'options': {
            'dpi': '96',
            'margin-top': 5,
            'javascript-delay': 500,
        },
    }

    headers = {
        'Content-Type': 'application/json',  # This is important
    }

    response = requests.post(
        wkhtml_ws_url,
        data=json.dumps(data),
        headers=headers,
    )

    if response.status_code != 200:
        raise Exception('Could not create PDF: status code: {}'.format(
            response.status_code))

    return ContentFile(response.content,
                       name=get_extract_file_name(subscription))


def get_extract_file_name(subscription):
    return "Extrato-{}-{}.pdf".format(subscription.person.name,
                                      subscription.event.slug, subscription.pk)
