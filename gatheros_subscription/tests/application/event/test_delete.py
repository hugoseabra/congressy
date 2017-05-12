from django.test import TestCase
from django.urls import reverse

from core.model.deletable import NotDeletableError
from gatheros_event.models import Event, Member


class EventDeleteTest(TestCase):
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
        '005_lot',
        '006_subscription',
    ]

    def setUp(self):
        self.event_pk = 6

    def _remove_subscriptions(self):
        event = Event.objects.get(pk=self.event_pk)
        for lot in event.lots.all():
            [sub.delete() for sub in lot.subscriptions.all() if sub]

    def _get_delete_url(self):
        return reverse(
            'gatheros_event:event-delete',
            kwargs={'pk': self.event_pk}
        )

    def _get_login_url(self):
        return reverse('gatheros_front:login')

    def _get_event_list_url(self):
        return reverse('gatheros_event:event-list')

    def _event_exists(self):
        return Event.objects.filter(pk=self.event_pk).exists()

    def _switch_context(self, group):
        member = self._get_event_member(group=group)
        organization = member.organization

        url = reverse('gatheros_event:organization-switch')
        self.client.post(url, {'organization-context-pk': organization.pk})

    def _get_event_member(self, group):
        assert self._event_exists() is True
        event = Event.objects.get(pk=self.event_pk)
        return event.organization.members.filter(group=group).first()

    def _get_user(self, group):
        member = self._get_event_member(group=group)
        assert member is not None
        user = member.person.user
        user.is_active = True
        user.save()
        return user

    def _event_owner_login(self):
        user = self._get_user(Member.ADMIN)
        assert user is not None
        assert self.client.login(testcase_user=user)
        self._switch_context(group=Member.ADMIN)

    def _event_helper_login(self):
        user = self._get_user(group=Member.HELPER)
        assert user is not None
        assert self.client.login(testcase_user=user)
        self._switch_context(group=Member.HELPER)

    def _process_delete(self, remove=True):
        if remove:
            self._remove_subscriptions()

        return self.client.post(self._get_delete_url())

    def test_delete_requires_login(self):
        url = self._get_delete_url()
        self.assertTrue(self._event_exists())

        # NOT Authenticated
        result = self._process_delete()
        self.assertRedirects(result, self._get_login_url() + '?next=' + url)

        # Authenticated
        self._event_owner_login()

        self.assertTrue(self._event_exists())
        result = self._process_delete()
        self.assertFalse(self._event_exists())
        self.assertRedirects(result, self._get_event_list_url())

    def test_event_with_subscriptions_cannot_be_deleted(self):
        self._event_owner_login()

        self.assertTrue(self._event_exists())

        with self.assertRaises(NotDeletableError):
            result = self._process_delete(remove=False)
            self.assertTrue(self._event_exists())
            self.assertRedirects(result, self._get_event_list_url())

        # Processando com remoção de inscrições
        self.assertTrue(self._event_exists())
        result = self._process_delete()
        self.assertFalse(self._event_exists())
        self.assertRedirects(result, self._get_event_list_url())

    def test_owner_deletes_event_and_returns_success(self):
        self._event_owner_login()

        self.assertTrue(self._event_exists())
        result = self._process_delete()
        self.assertFalse(self._event_exists())
        self.assertRedirects(result, self._get_event_list_url())

    def test_helper_deletes_event_and_returns_error(self):
        self._event_helper_login()

        self.assertTrue(self._event_exists())
        result = self._process_delete()
        self.assertEqual(result.status_code, 403)
        self.assertTrue(self._event_exists())
