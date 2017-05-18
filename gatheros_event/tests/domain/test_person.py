from django.contrib.auth.models import User
from kanu_locations.models import City

from core.tests import GatherosTestCase
from gatheros_event.models import Member, Person
from gatheros_event.models.rules import person as rule


class PersonModelTest(GatherosTestCase):
    fixtures = [
        'kanu_locations_city_test',
        '003_occupation',
        '004_category',
        '005_user',
        '006_person',
        '007_organization',
        '008_member'
    ]

    def _get_person_with_no_user(self):
        return Person.objects.get(pk='e50e56e7-2686-497f-82b1-a2500243f12b')

    def _get_person_with_internal_organization(self):
        return Person.objects.get(pk='a7c5f518-7669-4b71-a83b-2a7107e9c313')

    def _get_person_with_external_organization(self):
        return Person.objects.get(pk='5c76d747-f22a-4d27-9211-3b9929fb908d')

    def _create_person(self, persist=True, **kwargs):
        data = {
            'name': 'Test',
            'gender': 'M',
            'city': City.objects.get(pk=5413)
        }
        return self._create_model(
            model_class=Person,
            data=data,
            persist=persist,
            **kwargs
        )

    def test_rule_1_has_user_deve_ter_email(self):
        rule_callback = rule.rule_1_has_user_deve_ter_email

        person = self._get_person_with_no_user()
        person.has_user = True

        """ REGRA """
        self._trigger_validation_error(callback=rule_callback, params=[person],
                                       field='email')

        """ MODEL """
        self._trigger_validation_error(callback=person.save, field='email')

    def test_rule_2_ja_existe_outro_usuario_com_mesmo_email(self):
        rule_callback = rule.rule_2_ja_existe_outro_usuario_com_mesmo_email

        user = User.objects.first()

        person = self._get_person_with_no_user()
        person.has_user = True
        person.email = user.email

        """ REGRA """
        self._trigger_validation_error(callback=rule_callback, params=[person],
                                       field='email')

        """ MODEL """
        self._trigger_validation_error(callback=person.save, field='email')

    def test_rule_3_nao_remove_usuario_uma_vez_relacionado(self):
        rule_callback = rule.rule_3_nao_remove_usuario_uma_vez_relacionado

        person = self._get_person_with_no_user()
        person.has_user = True
        person.email = 'myemali@gmail.com'
        person.save()

        # Retorna como 'sem usuário'
        person.has_user = False

        """ REGRA """
        self._trigger_validation_error(callback=rule_callback, params=[person],
                                       field='has_user')

        """ MODEL """
        self._trigger_validation_error(callback=person.save, field='has_user')

    def test_rule_4_desativa_usuario_ao_deletar_pessoa(self):
        rule_callback = rule.rule_4_desativa_usuario_ao_deletar_pessoa

        def create_person_with_active_user():
            person = self._get_person_with_no_user()
            person.has_user = True
            person.email = str(person.pk) + '@gmail.com'
            person.save()

            # Ativa usuário para teste
            self.assertFalse(person.user.is_active)
            person.user.is_active = True
            person.user.save()

            return person

        """ REGRA """
        person = create_person_with_active_user()
        rule_callback(person)
        self.assertFalse(person.user.is_active)

        """ MODEL """
        person = create_person_with_active_user()
        user_pk = person.user.pk
        person.delete()
        user = User.objects.get(pk=user_pk)
        self.assertFalse(user.is_active)

    def test_cpf_invalido(self):
        person = self._create_person(cpf='84188838737', persist=False)

        self._trigger_validation_error(callback=person.save, field='cpf')

        # CPF válido
        cpf = '85188838737'
        person.cpf = cpf
        person.save()
        self.assertEqual(person.cpf, cpf)

    def test_telefone_invalido(self):
        person = self._create_person(phone='98552558555', persist=False)
        person.phone = '9855255a as b55'

        self._trigger_validation_error(callback=person.save, field='phone')

        # Phone válido
        phone = "62996558588"
        person.phone = phone
        person.save()

    def test_email_invalido(self):
        person = self._create_person()

        # Sem nick e @
        person.email = 'gmail.com'
        self._trigger_validation_error(callback=person.save, field='email')

        # Sem . após servidor
        person.email = 'me@gmail'
        self._trigger_validation_error(callback=person.save, field='email')

        # Email correto
        email = 'me@gmail.com'
        person.email = email
        self.assertEqual(person.email, email)

    def test_muda_nome_de_pessoa_e_de_organizacao(self):
        # Test if internal organization name is edited
        person = self._get_person_with_internal_organization()
        person.name = 'Edited name'
        person.save()

        member = person.members.filter(organization__internal=True).first()
        self.assertIsNotNone(member)

        organization = member.organization

        self.assertEqual(member.group, Member.ADMIN)
        self.assertEqual(person.name, organization.name)

        # Test if external organization name is edited
        person = self._get_person_with_external_organization()

        member = person.members.filter(group=Member.ADMIN,
                                       organization__internal=False).first()
        self.assertIsNotNone(member)

        person.name = 'Edited name'
        person.save()

        organization = member.organization
        org_name = organization.name

        self.assertNotEqual(person.name, organization.name)
        self.assertNotEqual(person.name, org_name)

    def test_muda_nome_de_pessoa_e_de_usuario(self):
        person = self._create_person(
            name='Another Test',
            has_user=True,
            email='me@gmail.com'
        )
        self.assertIsNotNone(person.user)
        self.assertEqual(person.name, person.user.get_full_name())

        person.name = 'Edited name'
        person.save()
        self.assertEqual(person.name, person.user.get_full_name())
