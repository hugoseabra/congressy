# test_edit_type_resend_invitation
# membro_deve_possuir_um_convite_antes_de_existir


# test_internal_edition_not_allowed

from django.contrib.auth.models import User
from django.test import TestCase

from gatheros_event.models import Organization


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

    def test_admin_can_delete(self):
        self.assertTrue(self.organization.is_admin(self.user))
        self.assertTrue(self.user.has_perm('gatheros_event.delete_member',
                                           self.organization.members.first()))
