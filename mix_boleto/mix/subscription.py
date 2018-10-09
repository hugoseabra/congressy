from django.db.models import Q
from django.db.transaction import atomic
from kanu_locations.models import City

from core.util.string import clear_string
from gatheros_event.models import Person
from gatheros_subscription.models import Subscription
from mix_boleto.models import SyncSubscription
from .boleto import MixBoleto
from .connection import MixConnection


class MixSubscription(object):
    """
    Sincroniza o estado de uma inscrição na MixEvents junto a Congressy,
    gerando uma inscrição de participantes equivalente.
    """

    def __init__(self,
                 mix_subscription_id,
                 mix_category,
                 mix_lot,
                 created,
                 updated):
        self.mix_subscription_id = mix_subscription_id
        self.mix_category = mix_category
        self.mix_lot = mix_lot

        self.created = created
        self.updated = updated

        self.sync_subscription = None
        self.cgsy_subscription = None

        self.person_data = {}
        self.boletos = []

    def set_person_data(self,
                        name,
                        gender=None,
                        email=None,
                        cpf=None,
                        phone=None,
                        street=None,
                        complement=None,
                        number=None,
                        village=None,
                        zip_code=None,
                        city=None,
                        uf=None,
                        institution=None,
                        cnpj=None):

        if cnpj:
            cnpj = clear_string(str(cnpj)).zfill(14)

        if cnpj:
            name = '{} - {}'.format(name, cnpj)

        if cpf:
            cpf = clear_string(str(cpf)).zfill(11)

        self.person_data = {
            'name': name,
            'gender': gender,
            'email': email,
            'cpf': cpf,
            'phone': phone,
            'street': street,
            'complement': complement,
            'number': number,
            'village': village,
            'zip_code': zip_code,
            'city': city,
            'uf': uf,
            'institution': institution,
            'institution_cnpj': cnpj,
        }

    def add_boleto(self, boleto: MixBoleto):
        if not isinstance(boleto, MixBoleto):
            return

        self.boletos.append(boleto)

    def sync_all(self, db: MixConnection):
        self.mix_category.sync(db)
        self.mix_lot.sync()
        self.sync(db)
        self.sync_boletos(db)

    def sync(self, db: MixConnection):

        self._check_person_required_fields()

        with atomic():
            try:
                self.sync_subscription = SyncSubscription.objects.get(
                    mix_subscription_id=self.mix_subscription_id,
                    sync_resource_id=db.sync_resource_id,
                )

                try:
                    self.cgsy_subscription = Subscription.objects.get(
                        pk=self.sync_subscription.cgsy_subscription_id,
                    )

                except Subscription.DoesNotExist:
                    self.cgsy_subscription = self._create_subscription()
                    self.sync_subscription.cgsy_subscription_id = \
                        self.cgsy_subscription.pk
                    self.sync_subscription.save()

                self.cgsy_subscription.person = self._create_updated_person()

                if self.cgsy_subscription.lot != self.mix_lot.lot:
                    self.cgsy_subscription.lot = self.mix_lot.lot

                self.cgsy_subscription.save()

            except SyncSubscription.DoesNotExist:
                self.cgsy_subscription = self._create_subscription()

                self.sync_subscription = SyncSubscription.objects.create(
                    sync_resource_id=db.sync_resource_id,
                    mix_subscription_id=self.mix_subscription_id,
                    cgsy_subscription_id=self.cgsy_subscription.pk,
                    mix_created=self.created,
                    mix_updated=self.updated,
                )

        self.created = self.sync_subscription.mix_created
        self.updated = self.sync_subscription.mix_updated

    def sync_boletos(self, db: MixConnection):
        for mix_boleto in self.boletos:
            # se já foi pago
            if mix_boleto.id_caixa:
                continue

            mix_boleto.sync(db, self)

            transaction = mix_boleto.transaction
            if transaction is not None and not transaction.paid:
                break

    def _create_subscription(self):
        person = self._create_updated_person()
        lot = self.mix_lot.lot

        return Subscription.objects.create(
            event=lot.event,
            lot=lot,
            person=person,
            created_by=1,
            completed=True,
            test_subscription=False,
        )

    def _create_updated_person(self):

        if not self.person_data:
            raise Exception('Nenhum dado de pessoa informado.')

        person_data = self.person_data.copy()

        city_name = None
        uf = None

        if 'city' in person_data:
            city_name = person_data.pop('city')

        if 'uf' in person_data:
            uf = person_data.pop('uf')

        person_qs = Person.objects.get_queryset()

        city = self._get_city(city_name=city_name, uf=uf)
        if not city:
            raise Exception('Cidade não encontrada: {}'.format(city_name))

        person_qs = person_qs.filter(city=city)

        if 'email' in person_data:
            person_qs = person_qs.filter(email=person_data.get('email'))

        if 'cpf' in person_data:
            person_qs = person_qs.filter(cpf=person_data.get('cpf'))

        try:
            person = person_qs.get()

            for key, value in person_data.items():
                if not value:
                    continue

                setattr(person, key, value)

            person.save()

        except Person.DoesNotExist:
            person_data['city'] = city
            person = Person.objects.create(**person_data)

        return person

    def _get_city(self, city_name=None, uf=None):

        if city_name:
            try:
                city_name = str(city_name).upper()
                city_qs = City.objects.filter(
                    Q(name=city_name) | Q(name_ascii=city_name)
                )

                if uf:
                    city_qs = city_qs.filter(uf=uf)

                return city_qs.get()

            except City.DoesNotExist:
                return None

    def _check_person_required_fields(self):
        required_fields = [
            'cpf',
            'phone',
            'street',
            'village',
            'zip_code',
            'city',
            'uf'
        ]

        for field in required_fields:
            if field not in self.person_data or not self.person_data[field]:
                raise Exception(
                    'Campo "{}" não informado. Os seguintes campos são'
                    ' obrigatórios: {}'.format(
                        field,
                        ', '.join(required_fields)
                    )
                )
