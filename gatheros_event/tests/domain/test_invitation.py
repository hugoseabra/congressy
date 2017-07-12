""" Testes de `Invitation` """
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.db.models import Count

from core.tests import GatherosTestCase
from gatheros_event.models import Invitation, Member, Organization, rules


class InvitationModelTest(GatherosTestCase):
    """ Testes de `Invitation` """
    fixtures = [
        '003_occupation',
        '005_user',
        '006_person',
        '007_organization',
        '008_member',
        '012_invitation',
    ]

    def _create_invitation(
        self,
        author=None,
        to=None,
        persist=False,
        **kwargs
    ):
        while to is None:
            if not author:
                author = Member.objects.filter(
                    organization__internal=False,
                    group=Member.ADMIN
                ).last()

            if not to:
                invitation_user_pks = [
                    e.to.pk for e in Invitation.objects.all()
                ]
                members_user_pks = [
                    e.person.user.pk for e in author.organization.members.all()
                ]

                pks = invitation_user_pks + members_user_pks
                pks.append(author.person.user.pk)
                to = User.objects.exclude(pk__in=pks).first()

        data = {
            'author': author,
            'to': to,
            'group': Member.ADMIN
        }
        return self._create_model(
            model_class=Invitation,
            data=data,
            persist=persist,
            **kwargs
        )

    def test_rule_1_organizacao_internas_nao_pode_ter_convites(self):
        rule = rules.invitation \
            .rule_1_organizacao_internas_nao_pode_ter_convites
        organization = Organization.objects.filter(internal=True).first()
        member = organization.members.filter(group=Member.ADMIN).first()
        user = User.objects.exclude(pk=member.person.user.pk).first()

        invitation = self._create_invitation(author=member, to=user)

        with self.assertRaises(IntegrityError):
            rule(invitation)

        with self.assertRaises(IntegrityError):
            invitation.save()

        """ FUNCIONANDO """
        organization.internal = False
        organization.save()
        invitation.save()

    def test_rule_2_nao_pode_mudar_autor(self):
        rule = rules.invitation.rule_2_nao_pode_mudar_autor
        invitation = Invitation.objects.filter(
            author__organization__internal=False
        ).first()

        invitation.author = Member.objects.filter(
            organization__internal=False
        ).exclude(pk=invitation.author.pk).first()

        with self.assertRaises(ValidationError):
            rule(invitation)

        with self.assertRaises(ValidationError):
            invitation.save()

    def test_rule_3_nao_pode_mudar_convidado(self):
        rule = rules.invitation.rule_3_nao_pode_mudar_convidado
        invitation = Invitation.objects.filter(
            author__organization__internal=False
        ).first()

        invitation.to = Member.objects \
            .filter(organization__internal=False).exclude(
                pk=invitation.author.pk,
                organization=invitation.author.organization
            ).first().person.user

        with self.assertRaises(ValidationError):
            rule(invitation)

        with self.assertRaises(ValidationError):
            invitation.save()

    def test_rule_4_administrador_nao_pode_se_convidar(self):
        rule = rules.invitation.\
            rule_4_administrador_nao_pode_se_convidar
        invitation = self._create_invitation()
        invited_user = invitation.to
        invitation.to = invitation.author.person.user

        with self.assertRaises(ValidationError):
            rule(invitation)

        with self.assertRaises(ValidationError):
            invitation.save()

        """ FUNCIONANDO """
        invitation.to = invited_user
        invitation.save()

    def test_rule_5_nao_deve_existir_2_convites_para_usuario_organizacao(self):
        rule = rules.invitation \
            .rule_5_nao_deve_existir_2_convites_para_mesmo_usuario
        first_invitation = self._create_invitation(persist=True)

        invitation = self._create_invitation(
            author=first_invitation.author,
            to=first_invitation.to
        )

        with self.assertRaises(ValidationError):
            rule(invitation)

        with self.assertRaises(ValidationError):
            invitation.save()

        """ FUNCIONANDO """
        first_invitation.delete()
        invitation.save()

    def test_rule_6_autor_deve_ser_membro_admin(self):
        rule = rules.invitation.rule_6_autor_deve_ser_membro_admin

        author = Member.objects.filter(group=Member.HELPER).first()
        invitation = self._create_invitation(author=author)

        with self.assertRaises(ValidationError):
            rule(invitation)

        with self.assertRaises(ValidationError):
            invitation.save()

    def test_rule_7_convidado_ja_membro_da_organizacao(self):
        rule = rules.invitation.\
            rule_7_nao_deve_convidar_um_membro_da_organizacao

        # Pegar alguma organização com mais de 1 membro
        organization = Organization.objects.annotate(
            num_members=Count('members')).filter(
            internal=False,
            num_members__gt=1
        ).first()

        members = organization.members
        author = members.filter(group=Member.ADMIN).first()
        invited = members.exclude(pk=author.pk).first()

        invitation = self._create_invitation(
            author=author,
            to=invited.person.user
        )

        with self.assertRaises(ValidationError):
            rule(invitation)

        with self.assertRaises(ValidationError):
            invitation.save()

    def test_no_invitation_for_internal_organization(self):
        invitation = Invitation(
            author=Member.objects.get(pk=1, group=Member.ADMIN),
            to=User.objects.get(pk=3),
            group=Member.ADMIN,
        )

        # Error when invitation from internal organization
        with self.assertRaises(IntegrityError):
            invitation.save()

    def invitation_has_already_been_created(self):
        # @todo rever teste, está desligado e confuso e não consegui arrumar
        member = Member.objects.get(pk=5, group=Member.ADMIN)
        invited = User.objects.get(pk=3)

        invitation = Invitation(
            author=member,  # Admin member
            to=invited,
            group=Member.ADMIN,
        )
        invitation.save()

        # Recreates invitation as new to check duplication
        invitation.pk = None

        with self.assertRaises(ValidationError) as e:
            invitation.save()

        self.assertTrue('to' in dict(e.exception).keys())

    def test_author_must_be_admin_member_of_organization(self):
        helper = Organization.objects.get(pk=5).get_members(
            group=Member.HELPER
        ).first()

        # Invitation created by helper
        invitation = Invitation(
            author=helper,
            to=User.objects.get(pk=6),
            group=Member.ADMIN,
        )

        # Error when a HELPER member creates an invitation
        with self.assertRaises(ValidationError) as e:
            invitation.save()

        self.assertTrue('author' in dict(e.exception).keys())

    def test_invited_not_member(self):
        member = Member.objects.get(pk=5, group=Member.ADMIN)
        organization = Organization.objects.get(pk=5)
        invited = User.objects.get(pk=3)

        def is_member():
            # Invited no member
            member_exists = False
            for invited_member in invited.person.members.all():
                if invited_member in organization.members.all():
                    member_exists = True

            return member_exists

        self.assertFalse(is_member())

        Member.objects.create(
            organization=organization,
            person=invited.person,
            group=Member.HELPER
        )
        self.assertTrue(is_member())

        # Invitation for an ALREADY MEMBER
        invitation = Invitation(
            author=member,  # Admin member
            to=invited,
            group=Member.ADMIN,
        )

        with self.assertRaises(ValidationError) as e:
            invitation.save()

        self.assertTrue('to' in dict(e.exception).keys())

    def test_invited_author_not_the_same(self):
        member = Member.objects.get(pk=5)

        invitation = Invitation(
            author=member,
            to=member.person.user,
            group=Member.ADMIN,
        )

        with self.assertRaises(ValidationError) as e:
            invitation.save()

        self.assertTrue('to' in dict(e.exception).keys())
