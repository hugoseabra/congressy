from django.contrib import messages
from django.core.exceptions import PermissionDenied, SuspiciousOperation
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import RedirectView

from gatheros_event.acl.gatheros_user_context import update_user_context
from gatheros_event.models import Organization


# @TODO Refatorar para inserir dados em sessão e mudança de contexto

class OrganizationSwitch(RedirectView):
    def post(self, request, *args, **kwargs):
        if not hasattr(request.user, 'person'):
            raise SuspiciousOperation('Usuário não possui vínculo com pessoa.')

        pk = request.POST.get('organization-context-pk', None)

        if not pk:
            messages.info(request, 'Nenhuma organização foi informada.')
            return self.get(request, *args, **kwargs)

        organization = get_object_or_404(Organization, pk=pk)
        if not organization.is_member(request.user.person):
            raise PermissionDenied('Você não é membro desta organização.')

        update_user_context(request, organization)

        if organization.internal is True:
            context = 'não está em organização'
        else:
            context = "está na organização '{}'".format(organization.name)

        messages.info(request, "Agora você {}.".format(context))

        return super(OrganizationSwitch, self).post(request, *args, **kwargs)

    def get_redirect_url(self, *args, **kwargs):
        return self.request.POST.get(
            'next',
            reverse_lazy('gatheros_front:start')
        )
