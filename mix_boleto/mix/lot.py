from datetime import datetime

from django.db.transaction import atomic

from gatheros_subscription.models import Lot


class MixLot(object):
    """
    Sincroniza o estado de um lot na Congressy a partir de um preço de
    categoria da MixEvents.
    """

    def __init__(self, mix_category, price, date_limit):
        self.mix_category = mix_category
        self.price = price
        self.date_limit = date_limit

        self.lot = None

    def sync(self):

        with atomic():

            try:
                self.lot = Lot.objects.get(
                    category_id=self.mix_category.cgsy_category.pk,
                    event_id=self.mix_category.event_id,
                    name=self._get_name()
                )

                if self.price:
                    self.lot.price = self.price

                self.lot.date_end = self.date_limit,
                self.lot.save()

            except Lot.DoesNotExist:
                self.lot = Lot.objects.create(
                    event_id=self.mix_category.event_id,
                    category=self.mix_category.cgsy_category,
                    date_start=datetime.now(),
                    date_end=self.date_limit,
                    name=self._get_name(),
                    active=True,
                )

                if self.price:
                    self.lot.price = self.price

                self.lot.save()

    def _get_name(self):
        return 'Limite {}'.format(self.date_limit.strftime('%d/%m/%Y'))
