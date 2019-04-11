""" Helper para gerar QRCode dentro do contexto de inscrições"""
import base64
import os
from tempfile import gettempdir

import qrcode
import qrcode.image.svg
from django.utils import six


def create_qrcode(subscription):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=5,
        border=0,
    )
    qr.add_data(subscription.pk)
    qr.make(fit=True)

    buffer = six.BytesIO()
    img = qr.make_image()
    img.save(buffer)

    return base64.b64encode(buffer.getvalue())


def get_qrcode_file_path(subscription):
    tmp_dir = os.path.join(gettempdir(), 'qrcodes')
    if not os.path.exists(tmp_dir):
        os.mkdir(tmp_dir)

    qrcode_file_path = os.path.join(
        tmp_dir,
        '{}.png'.format(subscription.code)
    )

    if not os.path.isfile(qrcode_file_path):
        content = create_qrcode(subscription)
        with open(qrcode_file_path, 'wb') as fh:
            fh.write(base64.b64decode(content.decode("utf-8")))
            fh.close()

    return qrcode_file_path
