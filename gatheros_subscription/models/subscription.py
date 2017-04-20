import uuid
from datetime import datetime
from django.db import IntegrityError, models
from django.db.models import Max

from gatheros_event.models import Event, Person
from . import Lot


class SubscriptionManager(models.Manager):
    def next_count(self, lot):
        count_max = self.filter(lot=lot).aggregate(Max('count'))
        if count_max['count__max']:
            return count_max['count__max'] + 1
        else:
            return 1

    def generate_code(self, event):
        while True:
            code = str(uuid.uuid4()).split('-')[0].upper()
            try:
                self.get(event=event, code=code)
            except Subscription.DoesNotExist:
                return code


# @TODO - verificar se evento irá emitir certificado. Se sim, exigir CPF da pessoa na inscrição

class Subscription(models.Model):
    DEVICE_ORIGIN_WEB = 'web'
    DEVICE_ORIGIN_OFFLINE = 'offline'

    DEVICE_ORIGINS = (
        (DEVICE_ORIGIN_WEB, 'WEB'),
        (DEVICE_ORIGIN_OFFLINE, 'Sincronização Off-line'),
    )

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, primary_key=True)
    person = models.ForeignKey(Person, verbose_name='pessoa', on_delete=models.CASCADE, related_name='subscriptions')
    event = models.ForeignKey(Event, verbose_name='evento', related_name='subscriptions', blank=True, editable=False)
    lot = models.ForeignKey(Lot, verbose_name='lote', related_name='subscriptions')
    origin = models.CharField(max_length=15, choices=DEVICE_ORIGINS, default='web', verbose_name='origem')
    created_by = models.PositiveIntegerField(verbose_name='criado por')

    attended = models.BooleanField(default=False, verbose_name='compareceu')
    code = models.CharField(max_length=15, blank=True, verbose_name='código')
    count = models.IntegerField(default=None, blank=True, verbose_name='num. inscrição')

    attended_on = models.DateTimeField(verbose_name='confirmado em', null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True, verbose_name='criado em')
    modified = models.DateTimeField(auto_now_add=True, verbose_name='modificado em')
    synchronized = models.BooleanField(default=False)

    objects = SubscriptionManager()

    class Meta:
        verbose_name = 'Inscrição'
        verbose_name_plural = 'Inscrições'
        ordering = ['person', 'event']
        unique_together = (("person", "event"), ("event", "code"),)

    def __str__(self):
        return '{} - {}'.format(self.person.name, self.event.name)

    def save(self, *args, **kwargs):
        if self.count is None:
            self.count = Subscription.objects.next_count(self.lot)

        self.event = self.lot.event

        if self.attended is True:
            self.attended_on = datetime.now()
        else:
            self.attended_on = None

        if self._state.adding:
            self.code = Subscription.objects.generate_code(self.event)

        self.full_clean()
        super(Subscription, self).save(*args, **kwargs)

    def clean(self):

        if self.lot.limit and int(self.lot.limit) > 0 and int(self.lot.subscriptions.count()) >= self.lot.limit:
            raise IntegrityError('Este lote atingiu o limite de inscrições.')

    def get_count_display(self):
        if not self.count:
            return '--'
        return '{0:03d}'.format(self.count)
