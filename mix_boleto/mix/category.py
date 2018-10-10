from django.db.transaction import atomic

from gatheros_subscription.models import LotCategory
from mix_boleto.models import SyncCategory
from .connection import MixConnection


class MixCategory(object):
    """
    Sincroniza o estado de uma categoria de participantes na MixEvents
    junto a Congressy, gerando uma categoria de participantes equivalente.
    """

    def __init__(self, event_id, id, name, created, updated):
        self.event_id = event_id
        self.mix_category_id = id
        self.name = name
        self.created = created
        self.updated = updated

        self.cgsy_category = None
        self.sync_category = None

    def sync(self, db: MixConnection):

        with atomic():
            try:
                self.sync_category = SyncCategory.objects.get(
                    mix_category_id=self.mix_category_id,
                    event_id=self.event_id,
                    sync_resource_id=db.sync_resource_id,
                )

                try:
                    self.cgsy_category = LotCategory.objects.get(
                        pk=self.sync_category.cgsy_category_id,
                    )

                except LotCategory.DoesNotExist:
                    self.cgsy_category = self._create_lot_category()
                    self.sync_category.cgsy_category_id = self.cgsy_category.pk
                    self.sync_category.save()

            except SyncCategory.DoesNotExist:
                self.cgsy_category = self._create_lot_category()

                self.sync_category = SyncCategory.objects.create(
                    sync_resource_id=db.sync_resource_id,
                    mix_category_id=self.mix_category_id,
                    cgsy_category_id=self.cgsy_category.pk,
                    event_id=self.event_id,
                    mix_created=self.created,
                    mix_updated=self.updated,
                )

        self.created = self.sync_category.mix_created
        self.updated = self.sync_category.mix_updated

    def _create_lot_category(self):
        return LotCategory.objects.create(
            event_id=self.event_id,
            name=self.name,
            active=True,
        )
