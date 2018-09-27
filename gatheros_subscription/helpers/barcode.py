""" Helper para gerar código de barras dentro do contexto de inscrições"""
import os
from tempfile import gettempdir
import base64

from barcode.codex import Code39
from barcode.writer import ImageWriter


def create_barcode(subscription):
    code = Code39(
        str(subscription.code),
        writer=ImageWriter(),
        add_checksum=False
    )
    code.writer.set_options(dict(dpi=130))
    code.default_writer_options['write_text'] = False
    options = dict(compress=True, quiet_zone=1, module_height=5.0)

    tmp_dir = os.path.join(gettempdir(), 'barcodes')
    if not os.path.exists(tmp_dir):
        os.mkdir(tmp_dir)

    barcode_path = os.path.join(tmp_dir, '{}.png'.format(subscription.code))

    if not os.path.isfile(barcode_path):
        barcode_path = code.save(barcode_path[0:-4], options)

    with open(barcode_path, 'rb') as f:
        read_data = f.read()
        f.close()

    return base64.b64encode(read_data)
