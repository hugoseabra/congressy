import os
from datetime import datetime

from django.core.exceptions import ValidationError
from django.db import models

from base.models import EntityMixin
from gatheros_event.models.mixins import GatherosModelMixin
from sync.helpers import check_file_sync_error


class SyncClient(GatherosModelMixin, EntityMixin, models.Model):
    class Meta:
        verbose_name = 'cliente de sincronização'
        verbose_name_plural = 'clientes de sincronização'

    event = models.ForeignKey(
        'gatheros_event.Event',
        on_delete=models.CASCADE,
        verbose_name='evento',
        related_name="sync_clients",
        # Making field required
        blank=False,
        null=False,
    )

    name = models.CharField(
        max_length=255,
        verbose_name='nome',
        # required
        blank=False,
        null=False,
    )

    key = models.CharField(
        max_length=40,
        verbose_name='chave',
        help_text='Chave de sincronização que libera a capacidade do cliente'
                  ' de sincronizar dados na plataforma.',
        # required
        blank=False,
        null=False,
        editable=False,
    )

    active = models.BooleanField(
        default=False,
        verbose_name='ativo'
    )

    last_sync = models.DateTimeField(
        auto_now_add=True,
        verbose_name='última sincronização',
        editable=False,
    )

    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name='criado em',
        editable=False,
    )

    modified = models.DateTimeField(
        auto_now=True,
        verbose_name='modificado em',
        editable=False,
    )

    def __str__(self):
        return '{} (ID: {})'.format(self.name, self.pk)


def get_file_path(instance, *args, **kwargs):
    """ Resgata localização onde os arquivos csv serão salvos. """

    now = datetime.now()
    day = str(now.day)
    month = str(now.month)
    year = str(now.year)
    hour = str(now.hour)
    minute = str(now.minute)

    if isinstance(instance, SyncClient):
        event_id = instance.event_id
    elif isinstance(instance, SyncQueue):
        event_id = instance.client.event_id
    else:
        event_id = 'NONE'

    filename = "SyncFile_{}-{}-{}_{}h{}m_{}.json".format(
        year,
        month,
        day,
        hour,
        minute,
        event_id
    )

    return os.path.join(
        "event",
        str(event_id),
        "sync_files",
        filename
    )


def validate_json_only_file(value):
    ext = os.path.splitext(value.name)[1]  # [0] returns path+filename

    valid_extensions = [
        '.json'
    ]

    if not ext.lower() in valid_extensions:
        raise ValidationError('Tipo de arquivo não permitido.')


class SyncQueue(GatherosModelMixin, EntityMixin, models.Model):
    class Meta:
        verbose_name = 'fila de sincronização'
        verbose_name_plural = 'filas de sincronização'

    NOT_STARTED_STATUS = 'not_started'
    RUNNING_STATUS = 'running'
    PROCESSED_STATUS = 'processed'
    CANCELLED_STATUS = 'processed'
    INVALID_STATUS = 'invalid'

    STATUSES = (
        (NOT_STARTED_STATUS, 'Não iniciado'),
        (RUNNING_STATUS, 'Em andamento'),
        (PROCESSED_STATUS, 'Processado'),
        (CANCELLED_STATUS, 'Cancelado'),
        (INVALID_STATUS, 'Inválido'),
    )

    client = models.ForeignKey(
        'sync.SyncClient',
        on_delete=models.CASCADE,
        verbose_name='cliente de sincronização',
        related_name="queues",
        # Making field required
        blank=False,
        null=False,
    )

    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name='criado em',
        editable=False,
    )

    modified = models.DateTimeField(
        auto_now=True,
        verbose_name='modificado em',
        editable=False,
    )

    file_path = models.FileField(
        upload_to=get_file_path,
        validators=[validate_json_only_file],
        verbose_name='arquivo de sincronização',
        help_text="Caminho do arquivo JSON a ser processado na sincronização",
        # required
        null=False,
        blank=False,
    )

    status = models.CharField(
        max_length=12,
        choices=STATUSES,
        default=NOT_STARTED_STATUS,
        verbose_name='Status',
        null=True,
    )

    error_message = models.TextField(
        verbose_name='Mensagens de erro',
        blank=True,
        null=True,
        editable=False,
    )

    warning_message = models.TextField(
        verbose_name='Mensagens de alerta',
        blank=True,
        null=True,
        editable=False,
    )

    def __str__(self):
        return '{} - {}'.format(self.client.name, self.created)

    def validate(self):
        try:
            self.error_message = None
            self.warning_message = None

            self.file_path.open()
            check_file_sync_error(self.file_path)

            if self.status == self.INVALID_STATUS:
                self.status = self.NOT_STARTED_STATUS

        except Exception as e:
            self.status = self.INVALID_STATUS
            self.error_message = str(e)

        # warning = get_sync_warning(self.file_path)

        # if warning is not None:
        #     self.warning_message = warning
