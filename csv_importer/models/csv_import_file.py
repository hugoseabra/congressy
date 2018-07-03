import os
from uuid import uuid4

from django.db import models

from csv_importer.validators import validate_csv_only_file


def get_file_path(instance, filename):
    """ Resgata localização onde os arquivos csv serão salvos. """
    return os.path.join('event', str(instance.event.id), filename)


class CSVImportFile(models.Model):
    ENCODING_UTF8 = "utf-8"
    ENCODING_8859_1 = "iso-8859-1"

    ENCODING_CHOICES = (
        (ENCODING_UTF8, "UTF-8"),
        (ENCODING_8859_1, "ISO 8859-1(Latim)")
    )

    uuid = models.UUIDField(
        default=uuid4,
        editable=False,
        unique=True,
        primary_key=True
    )

    event = models.ForeignKey(
        'gatheros_event.Event',
        on_delete=models.CASCADE,
        verbose_name='evento',
        related_name='csv_file'
    )

    csv_file = models.FileField(
        upload_to=get_file_path,
        validators=[validate_csv_only_file],
    )

    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name='criado em'
    )

    separator = models.CharField(
        max_length=1,
        default='"',
        verbose_name="separador",
    )

    delimiter = models.CharField(
        max_length=1,
        default=",",
        verbose_name="delimitador",
    )

    encoding = models.CharField(
        choices=ENCODING_CHOICES,
        default=ENCODING_UTF8,
        max_length=10,
        verbose_name="tipo de codificação",
    )
