from datetime import datetime
from decimal import Decimal

from django.core.management.base import BaseCommand

from mix_boleto.mix.category import MixConnection, MixCategory
from mix_boleto.mix.lot import MixLot
from mix_boleto.models import SyncResource


class Command(BaseCommand):
    help = 'Sincroniza categoria da MixEvents.'

    def handle(self, *args, **options):
        credencials = SyncResource.objects.get(pk=1)
        db = MixConnection(
            sync_resource_id=credencials.pk,
            host=credencials.host,
            user=credencials.user,
            password=credencials.password,
            db_name=credencials.db_name
        )
        db.connect()

        mix_cat = MixCategory(
            event_id=424,
            id=2,
            name='Participantes',
            created=datetime.strptime(
                '2017-09-02 12:11:16',
                "%Y-%m-%d %H:%M:%S"
            ),
            updated=datetime.strptime(
                '2017-11-09 14:49:57',
                "%Y-%m-%d %H:%M:%S"
            ),
        )

        mix_lot = MixLot(
            mix_category=mix_cat,
            price=Decimal(10.00),
            date_limit=datetime.strptime('2018-12-22', "%Y-%m-%d"),
        )

        mix_cat.sync(db)
        mix_lot.sync()

        db.close()
