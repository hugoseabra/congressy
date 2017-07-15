from core.tests import GatherosTestCase
from gatheros_event.models import Organization
from gatheros_subscription.models import Answer, Field, Subscription


class FieldModelTest(GatherosTestCase):
    """ Testes do model `Field` """
    fixtures = [
        'kanu_locations_city_test',
        '005_user',
        '006_person',
        '007_organization',
        '009_place',
        '010_event',
        '003_form',
        '004_field',
        '006_lot',
        '007_subscription',
        '008_answer',
    ]

    # noinspection PyMethodMayBeStatic
    def _get_organization(self):
        return Organization.objects.first()

    def _create_field(self, label, org=None, persist=False, **kwargs):
        if not org:
            org = self._get_organization()

        data = {
            'organization': org,
            'field_type': Field.FIELD_INPUT_TEXT,
            'label': label
        }
        return self._create_model(
            model_class=Field,
            data=data,
            persist=persist,
            **kwargs
        )

    def test_slug(self):
        """ Testa criação de slug. """

        field = self._create_field(label='New one', persist=True)
        self.assertEqual(field.name, 'new-one')

        field = self._create_field(label='New one', persist=True)
        self.assertEqual(field.name, 'new-one-1')

        field = self._create_field(label='New one', persist=True)
        self.assertEqual(field.name, 'new-one-2')

        field.label = 'Other one'
        field.save()
        self.assertEqual(field.name, 'other-one')

    def test_get_person_attribute_value(self):
        """
        Testa resgate de valor da instância de `Person` de uma inscrição.
        """
        organization = self._get_organization()
        subscription = Subscription.objects.filter(
            event__organization=organization
        ).first()
        f_name = Field.objects.get(name='name', organization=organization)

        person_name = f_name.get_person_attribute_value(subscription.person)
        self.assertEqual(person_name, subscription.person.name)

        # Um campo reservado de person não pode ser encontrado
        field = self._create_field(label='UUID', org=organization)
        person_uuid = field.get_person_attribute_value(subscription.person)
        self.assertIsNone(person_uuid)

        # Campo relacionável de person tb não pode ser resgatado
        field = self._create_field(label='subscriptions', org=organization)
        person_subs = field.get_person_attribute_value(subscription.person)
        self.assertIsNone(person_subs)

    def test_answer(self):
        """ Testa resgate de resposta tanto de `Person` quanto de `Answer` """
        organization = self._get_organization()
        f_name = Field.objects.get(name='name', organization=organization)
        f_gender = Field.objects.get(name='gender', organization=organization)
        subscription = Subscription.objects.filter(
            event__organization=organization
        ).first()

        name = f_name.answer(subscription)
        gender = f_gender.answer(subscription)
        self.assertEqual(name, subscription.person.name)
        self.assertEqual(gender, subscription.person.gender)

        additional_field = Field.objects.filter(
            organization=organization,
            form_default_field=False
        ).first()

        # Campos adicionais devolvem instância de `Answer`
        answer = additional_field.answer(subscription)
        self.assertIsInstance(answer, Answer)

        # Resposta retornada deve estar diretamente relacionada com `Field`
        self.assertEqual(answer.field.pk, additional_field.pk)
