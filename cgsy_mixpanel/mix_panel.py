import mixpanel
from django.conf import settings
from django.contrib.auth.models import User

from cgsy_mixpanel.mix_panel_env import MixPanelEnvironment
from cgsy_mixpanel.mix_panel_event import MixPanelEvent
from cgsy_mixpanel.mix_panel_organization import MixPanelOrganization
from cgsy_mixpanel.mix_panel_user import MixPanelUser
from .helpers import create_user


def create_mixpanel(user: User):
    return MixPanel(create_user(user))


class MixPanel:
    def __init__(self, user: MixPanelUser):
        self.mixpanel = mixpanel.Mixpanel(token=settings.MIX_PANEL_TOKEN)
        self.user = user

        self.identity = None

    def track_environment(self, env: MixPanelEnvironment):
        self._identify()

        self.mixpanel.track(
            self.identity,
            'Versão do Sistema',
            dict(env)
        )

    def track_organization(self, organization: MixPanelOrganization):
        self._identify()

        self.mixpanel.track(
            self.identity,
            'Organização',
            dict(organization)
        )

    def track_event(self, event: MixPanelEvent):
        self.mixpanel.track(
            self.identity,
            'Evento',
            dict(event)
        )

    def track(self, track_name: str, data: dict = None):
        self._identify()

        kwargs = {
            'distinct_id': self.identity,
            'event_name': track_name,
        }

        if data:
            kwargs['properties'] = data

        self.mixpanel.track(**kwargs)

    def _identify(self):
        if self.identity:
            return

        self.identity = self.user.identity

        user_data = dict(self.user)
        del user_data['ID']

        self.mixpanel.people_set(self.identity, user_data)
