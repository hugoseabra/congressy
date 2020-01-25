""" Helper para inscrições. """

import base64
import json
import os
from datetime import datetime

import absoluteuri
import requests
from django.conf import settings
from django.core.files.base import ContentFile
from django.template.loader import render_to_string

from gatheros_subscription.helpers.report_payment import \
    PaymentReportCalculator
from installment.models import Contract


def get_logo():
    path = os.path.join(
        settings.BASE_DIR,
        'frontend',
        'static',
        'assets',
        'img',
        'logo_v3.png',
    )

    with open(path, 'rb') as f:
        read_data = f.read()
        f.close()

    return base64.b64encode(read_data)


def get_template_path():
    return 'pdf/extract.html'


def get_context(subscription, user):
    """
    Resgata contexto adequado para o template de voucher
    """

    event = subscription.event

    calculator = PaymentReportCalculator(subscription=subscription)

    context = {
        'base_url': absoluteuri.build_absolute_uri(settings.STATIC_URL),
        'logo': get_logo(),
        'event': event,
        'now': datetime.now(),
        'by': user.person.name,
        'person': subscription.person,
        'lot': subscription.lot,
        'organization': event.organization,
        'subscription': subscription,
        'lots': calculator.lots,
        'transactions': calculator.transactions,
        'has_manual': calculator.has_manual,
        'installments': calculator.installments,
        'full_prices': calculator.full_prices,
        'object': subscription,
        'contracts': Contract.objects.filter(
            subscription=subscription
        )
    }

    return context


def create_extract(subscription, user):
    wkhtml_ws_url = settings.WKHTMLTOPDF_WS_URL

    html = render_to_string(
        template_name='pdf/extract.html',
        context=get_context(subscription, user)
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
