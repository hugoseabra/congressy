import uuid
from datetime import timedelta

from django.core.exceptions import ValidationError
from django.db import IntegrityError, models

from gatheros_event.models import Event


class LotManager(models.Manager):
    def generate_promo_code(self, lot):
        while True:
            code = str(uuid.uuid4()).split('-')[0].upper()
            try:
                self.get(promo_code=code)
            except Lot.DoesNotExist:
                return code


class Lot(models.Model):
    INTERNAL_DEFAULT_NAME = 'default'

    DISCOUNT_TYPE = (
        ('percent', '%'),
        ('money', 'R$'),
    )

    name = models.CharField(max_length=255, verbose_name='nome')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, verbose_name='evento', related_name='lots')
    date_start = models.DateTimeField(verbose_name='data inicial')
    date_end = models.DateTimeField(verbose_name='data final', null=True, blank=True)
    limit = models.PositiveIntegerField(null=True, blank=True, verbose_name='vaga(s)')
    price = models.DecimalField(max_digits=8, null=True, blank=True, decimal_places=2, verbose_name='preco')
    tax = models.DecimalField(max_digits=5, null=True, blank=True, decimal_places=2, verbose_name='taxa')
    discount_type = models.CharField(max_length=15, choices=DISCOUNT_TYPE, default='percent',
                                     verbose_name='tipo de desconto', null=True, blank=True)
    discount = models.DecimalField(max_digits=8, null=True, blank=True, decimal_places=2, verbose_name='desconto')
    promo_code = models.CharField(max_length=15, null=True, blank=True, verbose_name='código promocional', )
    transfer_tax = models.BooleanField(default=False, verbose_name='trasferir taxa para participante')
    private = models.BooleanField(default=False, verbose_name='privado')

    internal = models.BooleanField(default=False, verbose_name='gerado internamente')
    created = models.DateTimeField(auto_now_add=True, verbose_name='criado em')

    objects = LotManager()

    class Meta:
        verbose_name = 'lote'
        verbose_name_plural = 'lotes'
        ordering = ['pk', 'name', 'event']
        unique_together = (("name", "event"),)

    def save(self, **kwargs):
        if not self.date_end:
            self.date_end = self.event.date_start - timedelta(seconds=1)

        if self.private and not self.promo_code:
            self.promo_code = Lot.objects.generate_promo_code(self)

        self.full_clean()
        return super(Lot, self).save(**kwargs)

    def clean(self):
        # if new
        if self._state.adding and self.event.subscription_type == self.event.SUBSCRIPTION_SIMPLE and self.event.lots.count() > 0:
            raise IntegrityError(
                'O evento possui inscrições simples,'
                + ' Portanto, não é possível inserir mais de um lote no mesmo.'
            )

        if self.event.subscription_type == Event.SUBSCRIPTION_DISABLED:
            raise ValidationError({'event': ['O evento selecionado possui inscrições desativadas']})

        if self.date_start > self.event.date_start:
            raise ValidationError({'date_start': ['A data inicial do lote deve ser anterior a data inicial do evento']})

        if self.date_end and self.date_end > self.event.date_start:
            raise ValidationError({'date_end': ['A data final do lote deve ser anterior a data inicial do evento']})

        if self.date_end and self.date_start > self.date_end:
            raise ValidationError({'date_start': ['Data inicial do lote deve anterior a data final']})

        if self.event.subscription_type == self.event.SUBSCRIPTION_SIMPLE and self.internal is False:
            raise ValidationError(
                {'internal': ['O evento possui inscrições simples, portanto, o lote deve ser interno.']})

        if self.event.subscription_type == self.event.SUBSCRIPTION_SIMPLE and self.price:
            raise ValidationError({'price': ['O evento possui inscrições simples. O preço deve estar vazio.']})

        if self.event.subscription_type == self.event.SUBSCRIPTION_BY_LOTS and self.internal is True:
            raise ValidationError(
                {'internal': ['O evento possui inscrições por lotes, portanto o lote não pode ser interno.']}
            )

        if self.internal and self.price:
            raise ValidationError({'price': ['Lotes internos devem ser gratuitos. Deixe o preço vazio.']})

        if self.price and not self.limit:
            raise ValidationError({'limit': ['Lotes com inscrições pagas devem possuir um limite de público.']})

    def __str__(self):
        return '{} - {}'.format(self.event.name, self.name)
