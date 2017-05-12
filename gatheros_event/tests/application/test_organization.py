from unittest import skip

from django.contrib.auth.models import User
from django.test import TestCase

from gatheros_event.models import Organization


class OrganizationModelTest(TestCase):
    @skip
    def test_internal_edition_not_allowed(self):
        pass


class OrganizationAdminInternalPermissionsTest(TestCase):
    fixtures = [
        '003_occupation',
        '005_user',
        '006_person',
        '007_organization',
        '008_member',
    ]

    def setUp(self):
        self.user = User.objects.get(username='lucianasilva@gmail.com')
        self.organization = Organization.objects.get(slug="luciana-silva")

    def test_admin_cannot_invite(self):
        self.assertTrue(self.organization.is_admin(self.user))
        self.assertFalse(self.user.has_perm('gatheros_event.can_invite',
                                            self.organization))


class OrganizationAdminNotInternalPermissionsTest(TestCase):
    fixtures = [
        '003_occupation',
        '005_user',
        '006_person',
        '007_organization',
        '008_member',
    ]

    def setUp(self):
        self.user = User.objects.get(username='flavia@in2web.com.br')
        self.organization = Organization.objects.get(slug="paroquias-unidas")

    def test_admin_can_invite(self):
        self.assertTrue(self.organization.is_admin(self.user))
        self.assertTrue(self.user.has_perm('gatheros_event.can_invite',
                                           self.organization))


class OrganizationMembersPermissionsTest(TestCase):
    fixtures = [
        '003_occupation',
        '005_user',
        '006_person',
        '007_organization',
        '008_member',
    ]

    def setUp(self):
        self.user = User.objects.get(username='lucianasilva@gmail.com')
        self.organization = Organization.objects.get(slug="mnt")

    def test_admin_cannot_invite(self):
        self.assertFalse(self.organization.is_admin(self.user))
        self.assertFalse(self.user.has_perm('gatheros_event.can_invite',
                                            self.organization))


class OrganizationNotMembersPermissionsTest(TestCase):
    fixtures = [
        '003_occupation',
        '005_user',
        '006_person',
        '007_organization',
        '008_member',
    ]

    def setUp(self):
        self.user = User.objects.get(username='lucianasilva@gmail.com')
        self.organization = Organization.objects.get(slug="paroquias-unidas")

    def test_not_member_cannot_invite(self):
        self.assertFalse(self.organization.is_member(self.user))
        self.assertFalse(self.user.has_perm('gatheros_event.can_invite',
                                            self.organization))
