""" Helper para gerar QRCode dentro do contexto de inscrições"""
import base64

import qrcode
import qrcode.image.svg
from django.utils import six


def create_qrcode(subscription):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=5,
        border=4,
    )
    qr.add_data(subscription.pk)
    qr.make(fit=True)

    buffer = six.BytesIO()
    img = qr.make_image()
    img.save(buffer)

    return base64.b64encode(buffer.getvalue())
