from datetime import datetime

from core.tests import GatherosTestCase
from gatheros_event.models import Member, Organization, Person
from gatheros_event.models.rules import member as rule


class MemberModelTest(GatherosTestCase):
    fixtures = [
        'kanu_locations_city_test',
        '003_occupation',
        '004_category',
        '005_user',
        '006_person',
        '007_organization',
        '008_member'
    ]

    def _get_organization(self, internal=False):
        return Organization.objects.filter(internal=internal).first()

    def _get_person(self, has_user=True):
        return Person.objects.filter(has_user=has_user).first()

    def _create_organization(self, internal=True, persist=True):
        data = {'name': 'Org Test', 'internal': internal}
        return self._create_model(
            Model=Organization,
            data=data,
            persist=persist
        )

    def _create_member(
            self,
            person=None,
            organization=None,
            group=Member.ADMIN,
            persist=True
    ):
        if person is None:
            person = self._get_person()

        if organization is None:
            organization = self._get_organization()

        data = {
            'organization': organization,
            'person': person,
            'group': group,
            'created_by': 1,
            'invited_on': datetime.now()
        }

        return self._create_model(Model=Member, data=data, persist=persist)

    def test_rule_1_membros_deve_ter_usuarios(self):
        rule_callback = rule.rule_1_membros_deve_ter_usuarios

        member = self._create_member(person=self._get_person(has_user=False),
                                     persist=False)

        """ REGRA """
        self._trigger_integrity_error(rule_callback, [member])

        """ MODEL """
        self._trigger_integrity_error(member.save)

        # Insere usuário
        member.person.has_user = True
        member.person.save()

        # Agora funciona
        member.save()

    def test_rule_2_organizacao_interna_apenas_1_membro(self):
        rule_callback = rule.rule_2_organizacao_interna_apenas_1_membro

        member = self._create_member(
            organization=self._get_organization(internal=True), persist=False)

        """ REGRA """
        self._trigger_integrity_error(rule_callback, [member])

        """ MODEL """
        self._trigger_integrity_error(member.save)

        # Muda organização do membro
        member.organization = self._get_organization(internal=False)

        # Agora funciona
        member.save()

    def test_rule_3_organizacao_interna_unico_membro_admin(self):
        rule_callback = rule.rule_3_organizacao_interna_unico_membro_admin

        # Pega uma pessoa sem usuário e logo cria um para ele
        person = self._get_person(has_user=False)
        person.has_user = True
        person.save()

        member = self._create_member(
            person=person,
            organization=self._create_organization(internal=True),
            group=Member.HELPER,
            persist=False
        )

        """ REGRA """
        self._trigger_integrity_error(rule_callback, [member, True])

        """ MODEL """
        self._trigger_integrity_error(member.save)

    def test_rule_4_nao_remover_member_organizacao_interna(self):
        rule_callback = rule.rule_4_nao_remover_member_organizacao_interna
        member = self._create_member(
            organization=self._create_organization(internal=True)
        )

        """ REGRA """
        self._trigger_integrity_error(rule_callback, [member])

        """ MODEL """
        self._trigger_integrity_error(member.delete)
