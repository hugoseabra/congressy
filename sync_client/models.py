from django.db import models
from django.utils.timezone import now

from base.models import EntityMixin
from gatheros_event.models.mixins import GatherosModelMixin


class SyncItem(GatherosModelMixin, EntityMixin, models.Model):
    class Meta:
        verbose_name = 'item de sincronização'
        verbose_name_plural = 'items de sincronização'
        unique_together = ('object_id', 'object_type',)

    CREATION = 'creation'
    EDITION = 'edition'
    DELETION = 'deletion'

    ACTION_TYPES = (
        (CREATION, 'Criação'),
        (EDITION, 'Edição'),
        (DELETION, 'Exclusão'),
    )

    MODEL_PERSON = 'gatheros_event.person'
    MODEL_SUBSCRIPTION = 'gatheros_subscription.subscription'
    MODEL_TRANSACTION = 'payment.transaction'
    MODEL_TRANSACTION_STATUS = 'payment.transaction_status'
    MODEL_ATTENDANCE_SERVICE = 'attendance.attendance_service'
    MODEL_CHECKIN = 'attendance.checkin'
    MODEL_CHECKOUT = 'attendance.checkout'

    MODEL_SURVEY_QUESTION = 'survey.question'
    MODEL_SURVEY_OPTION = 'survey.option'
    MODEL_SURVEY_AUTHOR = 'survey.author'
    MODEL_SURVEY_ANSWER = 'survey.answer'

    MODEL_TYPES = (
        (MODEL_PERSON, MODEL_PERSON),
        (MODEL_SUBSCRIPTION, MODEL_SUBSCRIPTION),
        (MODEL_TRANSACTION, MODEL_TRANSACTION),
        (MODEL_TRANSACTION_STATUS, MODEL_TRANSACTION_STATUS),
        (MODEL_ATTENDANCE_SERVICE, MODEL_ATTENDANCE_SERVICE),
        (MODEL_CHECKIN, MODEL_CHECKIN),
        (MODEL_CHECKOUT, MODEL_CHECKOUT),
    )

    process_type = models.CharField(
        max_length=10,
        verbose_name='tipo de processamento',
        choices=ACTION_TYPES,
        # required
        blank=True,
        null=True,
    )

    process_time = models.DateTimeField(
        verbose_name='data e hora de processamento',
        default=now,
        blank=True,
        null=False,
        editable=False,
    )

    object_type = models.TextField(
        verbose_name='Tipo de objeto',
        choices=MODEL_TYPES,
        # required
        blank=True,
        null=True,
    )

    object_id = models.TextField(
        verbose_name='ID do objeto',
        # required
        blank=True,
        null=True,
    )

    object_repr = models.TextField(
        verbose_name='Repr. do objeto',
        # required
        blank=True,
        null=True,
    )

    content = models.TextField(
        verbose_name='Conteúdo a ser sincronizado',
        blank=True,
        null=True,
    )

    def __str__(self):
        return '{} (ID: {})'.format(self.object_repr, self.object_id)
