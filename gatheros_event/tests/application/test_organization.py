from django.contrib.auth.models import User
from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase
from django.urls import reverse

from gatheros_event.models import Organization


class OrganizationPanelTest(TestCase):
    fixtures = [
        '003_occupation',
        '005_user',
        '006_person',
        '007_organization',
        '008_member',
    ]

    def setUp(self):
        self.user = User.objects.get(username='lucianasilva@gmail.com')
        self.client.force_login(self.user)
        self.url = reverse('gatheros_event:organization-panel')

    def test_status_is_302(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_status_is_200_ok(self):
        member = self.user.person.members.filter(
            organization__internal=False
        ).first()
        assert member is not None
        organization = member.organization
        self.client.post(
            reverse('gatheros_event:organization-switch'),
            {'organization-context-pk': organization.pk}
        )

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)


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
        self.assertFalse(
            self.user.has_perm(
                'gatheros_event.can_invite',
                self.organization
            )
        )

    def test_check_improperly_permission(self):
        with self.assertRaises(ImproperlyConfigured):
            self.assertFalse(
                self.user.has_perm(
                    'gatheros_event.can_invite',
                    self.user
                )
            )


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
        self.assertTrue(
            self.user.has_perm(
                'gatheros_event.can_invite',
                self.organization
            )
        )


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
        self.assertFalse(
            self.user.has_perm(
                'gatheros_event.can_invite',
                self.organization
            )
        )


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
        self.assertFalse(
            self.user.has_perm(
                'gatheros_event.can_invite',
                self.organization
            )
        )
