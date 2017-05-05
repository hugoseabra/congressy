from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.db.models import Count

from core.tests import GatherosTestCase
from gatheros_event.models import Invitation, Member, Organization
from gatheros_event.models.rules import invitation as rule


class InvitationModelTest(GatherosTestCase):
    fixtures = [
        '003_occupation',
        '005_user',
        '006_person',
        '007_organization',
        '008_member',
        '012_invitation',
    ]

    def _create_invitation( self, author=None, to=None, persist=False, **kwargs ):

        while to is None:
            if not author:
                author = Member.objects.filter(organization__internal=False, group=Member.ADMIN).last()

            if not to:
                invitation_user_pks = [pk for pk in map(lambda inv: inv.to.pk, Invitation.objects.all())]
                members_user_pks = [pk for pk in
                                    map(lambda member: member.person.user.pk, author.organization.members.all())]

                pks = invitation_user_pks + members_user_pks
                pks.append(author.person.user.pk)
                to = User.objects.exclude(pk__in=pks).first()

        data = {
            'author': author,
            'to': to,
            'type': Invitation.INVITATION_TYPE_ADMIN
        }
        return self._create_model(Model=Invitation, data=data, persist=persist, **kwargs)

    def test_rule_1_organizacao_internas_nao_pode_ter_convites( self ):
        rule_callback = rule.rule_1_organizacao_internas_nao_pode_ter_convites
        organization = Organization.objects.filter(internal=True).first()
        member = organization.members.filter(group=Member.ADMIN).first()
        user = User.objects.exclude(pk=member.person.user.pk).first()

        invitation = self._create_invitation(author=member, to=user)

        """ RULE """
        self._trigger_integrity_error(rule_callback, [invitation])

        """ MODEL """
        self._trigger_integrity_error(invitation.save)

        """ FUNCIONANDO """
        organization.internal = False
        organization.save()
        invitation.save()

    def test_rule_2_nao_pode_mudar_autor( self ):
        rule_callback = rule.rule_2_nao_pode_mudar_autor
        invitation = Invitation.objects.filter(author__organization__internal=False).first()
        invitation.author = Member.objects.filter(organization__internal=False).exclude(pk=invitation.author.pk).first()

        """ RULE """
        self._trigger_validation_error(rule_callback, [invitation], field='author')

        """ MODEL """
        self._trigger_validation_error(invitation.save, field='author')

    def test_rule_3_nao_pode_mudar_convidado( self ):
        rule_callback = rule.rule_3_nao_pode_mudar_convidado
        invitation = Invitation.objects.filter(author__organization__internal=False).first()
        invitation.to = Member.objects \
            .filter(organization__internal=False) \
            .exclude(pk=invitation.author.pk, organization=invitation.author.organization) \
            .first().person.user

        """ RULE """
        self._trigger_validation_error(rule_callback, [invitation], field='to')

        """ MODEL """
        self._trigger_validation_error(invitation.save, field='to')

    def test_rule_4_autor_convida_a_si_mesmo( self ):
        rule_callback = rule.rule_4_autor_convida_a_si_mesmo
        invitation = self._create_invitation()
        invited_user = invitation.to
        invitation.to = invitation.author.person.user

        """ RULE """
        self._trigger_validation_error(rule_callback, [invitation], field='to')

        """ MODEL """
        self._trigger_validation_error(invitation.save, field='to')

        """ FUNCIONANDO """
        invitation.to = invited_user
        invitation.save()

    def test_rule_5_convite_ja_existente( self ):
        rule_callback = rule.rule_5_convite_ja_existente
        invitation = self._create_invitation(persist=True)

        invitation2 = self._create_invitation(author=invitation.author, to=invitation.to)

        """ RULE """
        self._trigger_validation_error(rule_callback, [invitation2, True], field='to')

        """ MODEL """
        self._trigger_validation_error(invitation2.save, field='to')

        """ FUNCIONANDO """
        invitation.delete()
        invitation2.save()

    def test_rule_6_autor_deve_ser_membro_admin( self ):
        rule_callback = rule.rule_6_autor_deve_ser_membro_admin

        author = Member.objects.filter(group=Member.HELPER).first()
        invitation = self._create_invitation(author=author)

        """ RULE """
        self._trigger_validation_error(rule_callback, [invitation, True], field='author')

        """ MODEL """
        self._trigger_validation_error(invitation.save, field='author')

    def test_rule_7_convidado_ja_membro_da_organizacao( self ):
        rule_callback = rule.rule_7_convidado_ja_membro_da_organizacao

        # Pegar alguma organização com mais de 1 membro
        organization = Organization.objects.annotate(num_members=Count('members')).filter(
            internal=False,
            num_members__gt=1
        ).first()

        members = organization.members
        author = members.filter(group=Member.ADMIN).first()
        invited = members.exclude(pk=author.pk).first()

        invitation = self._create_invitation(author=author, to=invited.person.user)

        """ RULE """
        self._trigger_validation_error(rule_callback, [invitation, True], field='to')

        """ MODEL """
        self._trigger_validation_error(invitation.save, field='to')

    def no_invitation_for_internal_organization( self ):
        invitation = Invitation(
            author=Member.objects.get(pk=1, group=Member.ADMIN),
            to=User.objects.get(pk=3),
            type=Invitation.INVITATION_TYPE_ADMIN,
        )

        # Error when invitation from internal organization
        with self.assertRaises(IntegrityError) as e:
            invitation.save()

    def invitation_has_already_been_created( self ):
        member = Member.objects.get(pk=5, group=Member.ADMIN)
        invited = User.objects.get(pk=3)

        invitation = Invitation(
            author=member,  # Admin member
            to=invited,
            type=Invitation.INVITATION_TYPE_ADMIN,
        )
        invitation.save()

        # Recreates invitation as new to check duplication
        invitation.pk = None

        with self.assertRaises(ValidationError) as e:
            invitation.save()

        self.assertTrue('to' in dict(e.exception).keys())

    def author_must_be_admin_member_of_organization( self ):
        helper = Organization.objects.get(pk=5).members.filter(group=Member.HELPER).first()

        # Invitation created by helper
        invitation = Invitation(
            author=helper,
            to=User.objects.get(pk=6),
            type=Invitation.INVITATION_TYPE_ADMIN,
        )

        # Error when a HELPER member creates an invitation
        with self.assertRaises(ValidationError) as e:
            invitation.save()

        self.assertTrue('author' in dict(e.exception).keys())

    def invited_not_member( self ):
        member = Member.objects.get(pk=5, group=Member.ADMIN)
        organization = Organization.objects.get(pk=5)
        invited = User.objects.get(pk=3)

        def is_member():
            # Invited no member
            member_exists = False
            for member in invited.person.members.all():
                if member in organization.members.all():
                    member_exists = True

            return member_exists

        self.assertFalse(is_member())

        Member.objects.create(
            organization=organization,
            person=invited.person,
            group=Member.HELPER,
            created_by=1,
        )
        self.assertTrue(is_member())

        # Invitation for an ALREADY MEMBER
        invitation = Invitation(
            author=member,  # Admin member
            to=invited,
            type=Invitation.INVITATION_TYPE_ADMIN,
        )

        with self.assertRaises(ValidationError) as e:
            invitation.save()

        self.assertTrue('to' in dict(e.exception).keys())

    def invited_author_not_the_same( self ):
        member = Member.objects.get(pk=5)

        invitation = Invitation(
            author=member,
            to=member.person.user,
            type=Invitation.INVITATION_TYPE_ADMIN,
        )

        with self.assertRaises(ValidationError) as e:
            invitation.save()

        self.assertTrue('to' in dict(e.exception).keys())
