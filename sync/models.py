import os

from django.db import models

from base.models import EntityMixin
from gatheros_event.models.mixins import GatherosModelMixin


class SyncClient(GatherosModelMixin, EntityMixin, models.Model):
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

    file_path = models.TextField(
        verbose_name='descrição breve',
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

    invalidation_message = models.CharField(
        max_length=255,
        verbose_name='Motivo de invalidação',
        blank=True,
        null=True,
    )

    def __str__(self):
        return '{} - {}'.format(self.event.name, self.created)

    def synchronizable(self):
        if os.path.isfile(self.file_path) is False:
            self.status = self.INVALID_STATUS
            self.save()
            return False

        return True

