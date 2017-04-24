from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase

from gatheros_event.models import Invitation, Member, Organization


class InvitationModelTest(TestCase):
    fixtures = [
        '003_occupation',
        '005_user',
        '006_person',
        '007_organization',
        '008_member',
    ]

    def test_no_invitation_for_internal_organization(self):
        invitation = Invitation(
            author=Member.objects.get(pk=1, group=Member.ADMIN),
            to=User.objects.get(pk=3),
            type=Invitation.INVITATION_TYPE_ADMIN,
        )

        # Error when invitation from internal organization
        with self.assertRaises(IntegrityError) as e:
            invitation.save()

    def test_invitation_has_already_been_created(self):
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

    def test_invited_not_member(self):
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

    def test_author_must_be_admin_member_of_organization(self):
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

    def test_invited_author_not_the_same(self):
        member = Member.objects.get(pk=5)

        invitation = Invitation(
            author=member,
            to=member.person.user,
            type=Invitation.INVITATION_TYPE_ADMIN,
        )

        with self.assertRaises(ValidationError) as e:
            invitation.save()

        self.assertTrue('to' in dict(e.exception).keys())
