from django.contrib import messages
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import RedirectView

from gatheros_event.acl.gatheros_user_context import update_user_context
from gatheros_event.models import Organization


class NotAllowedOrganization(IntegrityError):
    def __init__(self, *args, **kwargs):
        super(NotAllowedOrganization, self).__init__(*args, **kwargs)


# @TODO Refatorar para inserir dados em sessão e mudança de contexto

class OrganizationSwitch(RedirectView):
    def post(self, request, *args, **kwargs):
        pk = request.POST.get('organization-context-pk', None)
        next_path = request.POST.get(
            'next',
            reverse_lazy('gatheros_front:home')
        )
        if not pk:
            return

        organization = get_object_or_404(Organization, pk=pk)
        update_user_context(request, organization)

        if organization.internal is True:
            context = 'não está em organização'
        else:
            context = "está na organização '{}'".format(organization.name)

        messages.info(request, "Agora você {}.".format(context))

        self.url = next_path
        return super(OrganizationSwitch, self).post(request, *args, **kwargs)
