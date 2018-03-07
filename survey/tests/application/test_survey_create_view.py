"""
    Tests for Survey Creation View
"""
from test_plus.test import TestCase

from gatheros_event.tests import MockFactory as EventMockFactory


class SurveyCreateViewTests(TestCase):
    """ Survey Creation View test implementation """

    def setUp(self):
        self.event_mock_factory = EventMockFactory()
        self.person = self.event_mock_factory.fake_person()
        self.organization = self.event_mock_factory.fake_organization()
        self.event_mock_factory.join_organization(self.organization,
                                                  self.person)

        self.event = self.event_mock_factory.fake_event(self.organization)

    def test_private_partner_registration_get_is_200_ok(self):
        """ Tests if GET requests are responding ok.  """

        self.assertLoginRequired(url='survey:survey-create',
                                 event_pk=self.event.pk)

        user1 = self.person.user
        # Logged in, must fetch normally.
        with self.login(username=user1.username, password='password'):
            self.get_check_200('survey:survey-create', event_pk=self.event.pk)


