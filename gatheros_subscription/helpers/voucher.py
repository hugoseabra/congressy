""" Helper para inscrições. """
import base64

from django.conf import settings
from django.contrib.staticfiles.storage import staticfiles_storage
from django.template import loader
from wkhtmltopdf.utils import render_to_temporary_file, convert_to_pdf

from gatheros_subscription.helpers.barcode import create_barcode
from gatheros_subscription.helpers.qrcode import create_qrcode


def get_logo():
    uri = staticfiles_storage.url('assets/img/logo_v3.png')
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

    context = {
        'qrcode': create_qrcode(subscription),
        # 'barcode': create_barcode(subscription),
        'logo': get_logo(),
        'event': event,
        'place': place,
        'person': subscription.person,
        'lot': subscription.lot,
        'organization': event.organization,
        'subscription': subscription,
    }

    return context


def create_voucher(subscription):
    tempfile = render_to_temporary_file(
        loader.get_template('pdf/voucher.html'),
        context=get_context(subscription)
    )

    return convert_to_pdf(
        filename=tempfile.name,
        cmd_options={
            'margin-top': 5,
            'javascript-delay': 500,
        }
    )


def get_voucher_file_name(subscription):
    return "{}-{}.pdf".format(subscription.event.slug, subscription.pk)
