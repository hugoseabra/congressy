from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.functional import SimpleLazyObject
from django.views.generic.base import View

from gatheros_event.helpers.account import (
    get_member,
    get_organization,
    get_organizations,
    is_participant,
)


class AccountMixin(LoginRequiredMixin, View):
    @property
    def is_participant(self):
        return is_participant(self.request)

    @property
    def organization(self):
        return SimpleLazyObject(lambda: get_organization(self.request))

    @property
    def member(self):
        return SimpleLazyObject(lambda: get_member(self.request))

    @property
    def organizations(self):
        return SimpleLazyObject(lambda: get_organizations(self.request))
