# pylint: disable=W5101
import uuid
from decimal import Decimal

from django.db import models

from base.models import EntityMixin
from core.model import track_data


@track_data('status')
class Payable(models.Model, EntityMixin):
    WAITING_FUNDS = 'waiting_funds'
    AVAILABLE = 'available'
    TRANSFERRED = 'transferred'

    STATUSES = (
        (WAITING_FUNDS, 'Aguardando saldo'),
        (AVAILABLE, 'Disponível'),
        (TRANSFERRED, 'Transferido'),
    )

    TYPE_CREDIT = 'credit'
    TYPE_REFUND = 'refund'

    TYPES = (
        (TYPE_CREDIT, 'Crédito'),
        (TYPE_REFUND, 'Estono'),
    )

    class Meta:
        verbose_name = 'Item pagável'
        verbose_name_plural = 'Itens pagáveis'

    def __str__(self):
        return 'ID: {}, Transaction: {} - {}'.format(self.pk,
                                                 self.transaction_id,
                                                 self.get_status_display())

    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        primary_key=True
    )

    transaction = models.ForeignKey(
        'payment.Transaction',
        on_delete=models.CASCADE,
        related_name='payables',
        null=False,
        editable=False,
        verbose_name='transação',
    )

    pagarme_id = models.PositiveIntegerField(
        null=False,
        editable=False,
        verbose_name='ID de recebível (pagar.me)',
    )

    status = models.CharField(
        default=WAITING_FUNDS,
        max_length=15,
        choices=STATUSES,
        null=False,
        verbose_name='status',
    )

    type = models.CharField(
        max_length=8,
        choices=TYPES,
        null=False,
        verbose_name='tipo',
    )

    installment = models.PositiveIntegerField(
        default=1,
        verbose_name='parcela',
        null=False,
        editable=False,
    )

    amount = models.DecimalField(
        default=Decimal(0.00),
        verbose_name='montante',
        decimal_places=10,
        max_digits=25,
        null=False,
    )

    fee = models.DecimalField(
        default=Decimal(0.00),
        verbose_name='custo de transação',
        decimal_places=10,
        max_digits=25,
        null=True,
    )

    antecipation_fee = models.DecimalField(
        default=Decimal(0.00),
        verbose_name='custo de antecipação',
        decimal_places=10,
        max_digits=25,
        null=True,
    )

    recipient_id = models.CharField(
        max_length=28,
        null=False,
        verbose_name='ID recebedor (pagar.me)',
    )

    created = models.DateTimeField(
        editable=False,
        null=False,
        verbose_name='criado em',
    )

    payment_date = models.DateTimeField(
        verbose_name='pago em',
        null=True,
    )

    modified = models.DateTimeField(
        verbose_name='modificado em',
        null=True,
    )

    next_check = models.DateField(
        verbose_name='próxima verificação em',
        null=True,
    )
