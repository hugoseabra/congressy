# pylint: disable=W5101
import uuid
from decimal import Decimal

from django.db import models

from base.models import EntityMixin
from core.model import track_data


@track_data('status', 'pagarme_id', 'fee', 'antecipation_fee',
            'payment_date', 'next_check')
class Payable(models.Model, EntityMixin):
    # Esse status significa que o cliente final ainda não realizou o pagamento.
    STATUS_WAITING_FUNDS = 'waiting_funds'

    # Significa que o valor da transação atrelada a esse recebível foi paga e,
    # portanto, esse valor está disponível para saque
    STATUS_PAID = 'paid'

    # Status intermediário antes do momento do pagamento
    STATUS_PREPAID = 'prepaid'

    # Recebível pertence à uma transação que está com status chargedback.
    # Sendo que o status só vai mudar caso o chargeback seja revertido.
    STATUS_SUSPENDED = 'suspended'

    STATUSES = (
        (STATUS_WAITING_FUNDS, 'Aguardando saldo'),
        (STATUS_PREPAID, 'Em processo de pagamento'),
        (STATUS_PAID, 'Pago (disponível)'),
        (STATUS_SUSPENDED, 'Suspenso'),
    )

    TYPE_CREDIT = 'credit'
    TYPE_REFUND = 'refund'
    TYPE_CHARGEBACK = 'chargeback'
    TYPE_CHARGEBACK_REFUND = 'chargeback_refund'
    TYPE_REFUND_REVERSAL = 'refund_reversal'
    TYPE_BLOCK = 'block'
    TYPE_UNBLOCK = 'unblock'

    TYPES = (
        (TYPE_CREDIT, 'Crédito'),
        (TYPE_REFUND, 'Estono'),
        (TYPE_CHARGEBACK, 'Chargeback'),
        (TYPE_CHARGEBACK_REFUND, 'Estono de chargeback'),
        (TYPE_BLOCK, 'Bloqueado'),
        (TYPE_UNBLOCK, 'Desbloqueado'),
    )

    class Meta:
        verbose_name = 'Item pagável'
        verbose_name_plural = 'Itens pagáveis'

    def __str__(self):
        return 'ID: {}, Transaction: {} - {} - {}'.format(
            self.pk,
            self.transaction_id,
            self.get_type_display(),
            self.get_status_display(),
        )

    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        primary_key=True
    )

    split_rule = models.ForeignKey(
        'payment.SplitRule',
        on_delete=models.CASCADE,
        related_name='payables',
        null=False,
        editable=False,
        verbose_name='regra de rateamento',
    )

    pagarme_id = models.CharField(
        max_length=28,
        null=False,
        editable=False,
        verbose_name='ID de recebível (pagar.me)',
    )

    status = models.CharField(
        default=STATUS_WAITING_FUNDS,
        max_length=15,
        choices=STATUSES,
        null=False,
        blank=True,
        verbose_name='status',
    )

    type = models.CharField(
        max_length=15,
        choices=TYPES,
        null=False,
        verbose_name='tipo',
    )

    installment = models.PositiveIntegerField(
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
        editable=False,
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

    next_check = models.DateTimeField(
        verbose_name='próxima verificação em',
        null=True,
    )
