from django.db import models
from gatheros_event.models import Event


class Lot(models.Model):
    DISCOUNT_TYPE = (
        ('percent', '%'),
        ('money', 'R$'),
    )

    name = models.CharField(max_length=255, verbose_name='nome')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, verbose_name='evento', related_name='lots')
    date_start = models.DateTimeField(verbose_name='data inicial')
    date_end = models.DateTimeField(verbose_name='data final', null=True, blank=True)
    limit = models.PositiveIntegerField(null=True, blank=True, verbose_name='limite')
    price = models.DecimalField(max_digits=8, null=True, blank=True, decimal_places=2, verbose_name='preco')
    tax = models.DecimalField(max_digits=5, null=True, blank=True, decimal_places=2, verbose_name='taxa')
    discount_type = models.CharField(max_length=15, choices=DISCOUNT_TYPE, default='percent',
                                     verbose_name='tipo de desconto', null=True, blank=True)
    discount = models.DecimalField(max_digits=8, null=True, blank=True, decimal_places=2, verbose_name='desconto')
    promo_code = models.CharField(max_length=15, null=True, blank=True, verbose_name='código promocional', )
    transfer_tax = models.BooleanField(default=False, verbose_name='trasferir taxa para participante')
    private = models.BooleanField(default=False, verbose_name='privado')

    internal = models.BooleanField(default=True, verbose_name='gerado internamente')
    created = models.DateTimeField(auto_now_add=True, verbose_name='criado em')

    class Meta:
        verbose_name = 'lote'
        verbose_name_plural = 'lotes'
        ordering = ['pk', 'name', 'event']

    def save(self, **kwargs):
        if not self.date_end:
            self.date_end = self.event.date_start
        return super(Lot, self).save(**kwargs)

    def __str__(self):
        return '{} - {}'.format(self.event.name, self.name)
