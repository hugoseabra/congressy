from datetime import datetime
from decimal import Decimal

from django.core.management.base import BaseCommand

from mix_boleto.mix.boleto import MixBoleto
from mix_boleto.mix.category import MixConnection, MixCategory
from mix_boleto.mix.lot import MixLot
from mix_boleto.mix.subscription import MixSubscription
from mix_boleto.models import SyncResource


class Command(BaseCommand):
    help = 'Sincroniza inscrição entre a MixEvents e Congressy.'

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

        mix_sub = MixSubscription(
            mix_subscription_id=1,
            mix_category=mix_cat,
            mix_lot=mix_lot,
            created=datetime.strptime(
                '2017-09-02 12:11:16',
                "%Y-%m-%d %H:%M:%S"
            ),
            updated=datetime.strptime(
                '2017-11-09 14:49:57',
                "%Y-%m-%d %H:%M:%S"
            ),
        )

        mix_sub.set_person_data(
            name='Hugo Seabra',
            gender='M',
            email='hugo@congressy.com',
            cpf='00177542160',
            phone='62996550852',
            street='Av San Martin',
            village='Jardim Novo Mundo',
            city='Goiânia',
            uf='GO',
            zip_code='74710040'
        )

        mix_boleto = MixBoleto(
            id=49,
            expiration_date=datetime.strptime('2018-10-06', "%Y-%m-%d"),
            amount='500',
            installments=5,
            installment_part=1,
            created=datetime.strptime(
                '2017-09-02 12:11:16',
                "%Y-%m-%d %H:%M:%S"
            ),
            updated=datetime.strptime(
                '2017-11-09 14:49:57',
                "%Y-%m-%d %H:%M:%S"
            ),
            link_boleto=None,
            id_caixa=None,
            cancelled=False,
        )

        mix_sub.sync_all(db)

        mix_boleto.sync(db, mix_sub)

        db.close()
