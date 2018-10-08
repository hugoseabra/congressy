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
                        institution=None):

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
        }

    def add_boleto(self, boleto: MixBoleto):
        if not isinstance(boleto, MixBoleto):
            return

        self.boletos.append(boleto)

    def sync_all(self, db: MixConnection):
        self.mix_category.sync(db)
        self.mix_lot.sync(db)
        self.sync_subscription(db)
        self.sync_boletos(db)

    def sync_subscription(self, db: MixConnection):

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
            mix_boleto.sync(db)

    def _create_subscription(self):

        person_qs = Person.objects.get_queryset()

        if 'email' in self.person_data:
            person_qs = person_qs.filter(cpf=self.person_data.get('email'))

        if 'cpf' in self.person_data:
            person_qs = person_qs.filter(cpf=self.person_data.get('cpf'))

        try:
            person = person_qs.get()

        except Person.DoesNotExist:
            person = Person.objects.create(**self.person_data)

        return Subscription.objects.create(
            lot=self.mix_lot.lot,
            person=person,
            created_by=1,
            completed=True,
            test_subscription=False,
        )
