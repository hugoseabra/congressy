from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import RedirectView
from datetime import datetime

from gatheros_event.helpers import account
from gatheros_event.models import Organization


class OrganizationSwitch(RedirectView):
    def post(self, request, *args, **kwargs):

        if not request.user.is_authenticated():
            return super(OrganizationSwitch, self).post(
                request,
                *args,
                **kwargs
            )

        pk = request.POST.get('organization-context-pk', None)

        if not pk:
            messages.info(request, 'Nenhuma organização foi informada.')
            return self.get(request, *args, **kwargs)

        organization = get_object_or_404(Organization, pk=pk, active=True)
        if not organization.is_member(request.user):
            messages.error(request, 'Você não é membro desta organização.')
            return super(OrganizationSwitch, self).post(
                request,
                *args,
                **kwargs
            )

        members = organization.members.filter(
            person__user=self.request.user,
            active=True
        )
        if not members:
            messages.error(request, 'Você não é membro desta organização.')
            return super(OrganizationSwitch, self).post(
                request,
                *args,
                **kwargs
            )

        account.update_account(request, organization)

        if organization.internal is True:
            context = 'não está em organização'
        else:
            context = "está na organização '{}'".format(organization.name)

        messages.info(request, "Agora você {}.".format(context))
        organization.last_access = datetime.now().strftime(
                "%Y-%m-%dT%H:%M:%S.%fZ")

        organization.save()
        return super(OrganizationSwitch, self).post(request, *args, **kwargs)

    def get_redirect_url(self, *args, **kwargs):
        return reverse_lazy('event:event-list')
