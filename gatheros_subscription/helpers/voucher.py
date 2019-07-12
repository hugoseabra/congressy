""" Helper para inscrições. """

import base64
import json
import os
from tempfile import gettempdir

import absoluteuri
import requests
from django.conf import settings
from django.contrib.staticfiles.storage import staticfiles_storage
from django.core.files.base import ContentFile
from django.template.loader import render_to_string

from gatheros_subscription.helpers.barcode import get_barcode_file_path
from gatheros_subscription.helpers.qrcode import get_qrcode_file_path


def get_logo():
    uri = staticfiles_storage.url('assets/img/logo_v4.png')
    url = settings.BASE_DIR + "/frontend" + uri
    with open(url, 'rb') as f:
        read_data = f.read()
        f.close()

    return base64.b64encode(read_data)


def get_template_path():
    return 'pdf/voucher.html'


def get_context(subscription):
    """
    Resgata contexto adequado para o template de voucher
    """

    event = subscription.event
    try:
        place = event.place
    except AttributeError:
        place = None

    barcode_file_path = get_barcode_file_path(subscription)
    with open(barcode_file_path, 'rb') as barcode_fh:
        barcode_content = base64.b64encode(barcode_fh.read()).decode('UTF-8')
        barcode_fh.close()

    with open(get_qrcode_file_path(subscription), 'rb') as qrcode_fh:
        qrcode_content = base64.b64encode(qrcode_fh.read()).decode('UTF-8')
        qrcode_fh.close()

    context = {
        'base_url': absoluteuri.build_absolute_uri(settings.STATIC_URL),
        'qrcode': qrcode_content,
        'barcode': barcode_content,
        'logo': get_logo(),
        'event': event,
        'place': place,
        'person': subscription.person,
        'lot': subscription.ticket_lot,
        'organization': event.organization,
        'subscription': subscription,
    }

    return context


def create_voucher(subscription, save=False, force=False):
    tmp_dir = os.path.join(gettempdir(), 'vouchers')
    if not os.path.exists(tmp_dir):
        os.mkdir(tmp_dir)

    voucher_file_path = os.path.join(
        tmp_dir,
        '{}.pdf'.format(subscription.code)
    )

    if save is True and force is False and os.path.isfile(voucher_file_path):
        return voucher_file_path

    wkhtml_ws_url = settings.WKHTMLTOPDF_WS_URL

    html = render_to_string(
        template_name='pdf/voucher.html',
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

    pdf_file = ContentFile(
        response.content,
        name=get_voucher_file_name(subscription)
    )

    if save is False:
        return pdf_file

    with open(voucher_file_path, 'wb') as f:
        pdf_file.open()
        f.write(pdf_file.read())
        f.close()
        pdf_file.close()

    return voucher_file_path


def get_voucher_file_name(subscription):
    return "{}-{}.pdf".format(subscription.event.slug, subscription.pk)
