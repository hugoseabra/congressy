""" Helper para gerar código de barras dentro do contexto de inscrições"""
import base64
import os
from io import BytesIO
from tempfile import gettempdir

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
    options = dict(compress=True, quiet_zone=1, module_height=8.0)

    image = code.render(options)

    in_mem_file = BytesIO()
    image.save(in_mem_file, format="PNG")
    # reset file pointer to start
    in_mem_file.seek(0)
    img_bytes = in_mem_file.read()

    return base64.b64encode(img_bytes)


def get_barcode_file_path(subscription):
    tmp_dir = os.path.join(gettempdir(), 'barcodes')
    if not os.path.exists(tmp_dir):
        os.mkdir(tmp_dir)

    barcode_file_path = os.path.join(
        tmp_dir,
        '{}.png'.format(subscription.code)
    )

    if not os.path.isfile(barcode_file_path):
        content = create_barcode(subscription)
        with open(barcode_file_path, 'wb') as fh:
            fh.write(base64.b64decode(content))
            fh.close()

    return barcode_file_path
