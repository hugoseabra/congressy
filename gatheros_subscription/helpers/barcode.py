""" Helper para gerar código de barras dentro do contexto de inscrições"""
import base64

import barcode
from barcode.writer import ImageWriter

def create_barcode(subscription):
    code = barcode.Code39(str(subscription.pk)[:-15], writer=ImageWriter())
    code.writer.set_options(dict(dpi=300))
    code.default_writer_options['write_text'] = False
    options = dict(compress=True)
    img = code.save('barcode')
    with open(img, 'rb') as f:
        read_data = f.read()
        f.close()

    return base64.b64encode(read_data)