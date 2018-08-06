import os
from datetime import datetime
from uuid import uuid4

from django.db import models
from django.utils import timezone

from importer.validators import validate_csv_only_file
from .storage import OverwriteStorage


def get_file_path(instance, *args, **kwargs):
    """ Resgata localização onde os arquivos csv serão salvos. """

    now = datetime.now()
    day = str(now.day)
    month = str(now.month)
    year = str(now.year)
    hour = str(now.hour)
    minute = str(now.minute)

    filename = "Import_Congressy_{}_{}_{}_{}h{}m.csv".format(
        day,
        month,
        year,
        hour,
        minute,
    )

    return os.path.join(
        "event",
        str(instance.event.id),
        "import",
        "csv",
        filename
    )


def get_err_file_path(instance, *args, **kwargs):
    """ Resgata localização onde os arquivos de erro do csv serão salvos. """

    now = datetime.now()
    day = str(now.day)
    month = str(now.month)
    year = str(now.year)
    hour = str(now.hour)
    minute = str(now.minute)

    filename = "Erros_de_Importação_Congressy_{}_{}_{}_{}h{}m.csv".format(
        day,
        month,
        year,
        hour,
        minute,
    )

    return os.path.join(
        "event",
        str(instance.event.id),
        "import",
        "csv",
        filename
    )


def get_correction_file_path(instance, *args, **kwargs):
    """ Resgata localização onde os arquivos de erro do csv serão salvos. """

    filename = "Import_Congressy_.csv"

    return os.path.join(
        "event",
        str(instance.event.id),
        "import",
        "csv",
        "fix_" + filename
    )


class CSVFileConfig(models.Model):
    """
        Representação de todas as configurações de leitura de um arquivo CSV
    """

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

    lot = models.ForeignKey(
        'gatheros_subscription.Lot',
        on_delete=models.CASCADE,
        verbose_name='lot',
        related_name='csv_file',
    )

    csv_file = models.FileField(
        upload_to=get_file_path,
        validators=[validate_csv_only_file],
        verbose_name="Arquivo CSV",
    )

    error_csv_file = models.FileField(
        upload_to=get_err_file_path,
        validators=[validate_csv_only_file],
        storage=OverwriteStorage(),
    )

    correction_csv_file = models.FileField(
        upload_to=get_correction_file_path,
        validators=[validate_csv_only_file],
        storage=OverwriteStorage(),
        null=True,
    )

    created = models.DateTimeField(
        verbose_name='criado em',
        editable=False,
    )

    modified = models.DateTimeField(
        verbose_name='modificado em'
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

    processed = models.BooleanField(
        default=False,
        verbose_name='arquivo já foi processado'
    )

    def save(self, *args, **kwargs):
        if not self.created:
            self.created = timezone.now()

        self.modified = timezone.now()
        return super().save(*args, **kwargs)

    def filename(self):
        return os.path.basename(self.csv_file.name)

    def err_filename(self):
        return os.path.basename(self.error_csv_file.name)
