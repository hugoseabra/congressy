from django.test import TestCase
from django.urls import reverse

from django.contrib.auth.models import User
from core.model.deletable import NotDeletableError
from gatheros_event.models import Event, Organization, Member


class OrganizationSwitchTest(TestCase):
    fixtures = [
        'kanu_locations_city_test',
        '005_user',
        '003_occupation',
        '004_category',
        '006_person',
        '007_organization',
        '008_member',
        '009_place',
        '010_event',
    ]

    def setUp(self):
        # Usuário com várias organizações
        self.user_pk = 4
        self.user_password = '123'
        self.url = reverse('gatheros_event:organization-switch')

    def _get_user(self):
        user = User.objects.get(pk=self.user_pk)
        assert user is not None
        user.set_password(self.user_password)
        user.save()
        return user

    def _login(self):
        user = self._get_user()
        assert self.client.login(
            username=user.username,
            password=self.user_password
        )
        return user

    def _get_user_context(self):
        return self.client.session['user_context']

    def _get_active_organization(self):
        uc = self._get_user_context()
        active = uc.get('active_organization')
        assert active
        assert active.get('pk') is not None
        return active

    def _get_organization(self):
        self._login()
        active = self._get_active_organization()
        assert active.get('pk') is not None

        organization = Organization.objects.get(pk=active.get('pk'))
        assert organization is not None
        return organization

    def _get_other_organization_pk(self, organization):
        user_context = self._get_user_context()
        orgs = user_context['organizations']
        assert len(orgs) > 1

        other = [org for org in orgs if org['pk'] != organization.pk][0]
        assert other.get('pk') is not None
        return other.get('pk')

    def _get_not_member_organization_pk(self):
        user_context = self._get_user_context()
        orgs = user_context['organizations']
        assert len(orgs) > 1

        pks = [org.get('pk') for org in orgs]
        return Organization.objects.exclude(pk__in=pks).first().pk

    def test_switch_organization(self):
        # First organization
        organization = self._get_organization()
        active = self._get_active_organization()
        self.assertEqual(active.get('pk'), organization.pk)

        # Switch
        other_pk = self._get_other_organization_pk(organization)
        self.client.post(self.url, {'organization-context-pk': other_pk})

        # Other organization
        organization = self._get_organization()
        active = self._get_active_organization()
        self.assertEqual(active.get('pk'), organization.pk)

    def test_not_allowed_organization(self):
        # First organization
        organization = self._get_organization()
        active = self._get_active_organization()
        self.assertEqual(active.get('pk'), organization.pk)

        # Switch
        other = self._get_not_member_organization_pk()
        result = self.client.post(self.url, {'organization-context-pk': other})
        self.assertEqual(result.status_code, 403)
