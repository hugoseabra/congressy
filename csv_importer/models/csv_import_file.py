import os
from uuid import uuid4

from django.db import models


def get_file_path(instance, filename):
    """ Resgata localização onde os arquivos csv serão salvos. """
    return os.path.join('event', str(instance.event.id), filename)


class CSVImportFile(models.Model):

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
    )

    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name='criado em'
    )

