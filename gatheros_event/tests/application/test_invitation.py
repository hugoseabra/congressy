# test_resend_invitation_differente_type(self):
# test_expiration_days_as_configured(self):
from django.contrib.auth.models import User
from django.test import TestCase

from gatheros_event.forms import InvitationForm


class InvitationFormTest(TestCase):
    fixtures = [
        '001_user',
        '003_occupation',
        '005_user',
        '006_person',
        '007_organization',
        '008_member',
    ]

    # noinspection PyMethodMayBeStatic
    def _get_form(self, username="lucianasilva@gmail.com", data=None):
        user = User.objects.get(username=username)
        return InvitationForm(user, data)

    def test_init_without_user(self):
        with self.assertRaises(TypeError):
            # noinspection PyArgumentList
            InvitationForm()

    def test_init_with_user_without_data(self):
        form = self._get_form(data={})
        self.assertFalse(form.is_valid())
        self.assertIn('organization', form.errors)
        self.assertIn('emails', form.errors)

    def test_renderinit_with_user_without_data(self):
        form = self._get_form(data={})
        self.assertFalse(form.is_valid())
        self.assertIn('organization', form.errors)
        self.assertIn('emails', form.errors)
