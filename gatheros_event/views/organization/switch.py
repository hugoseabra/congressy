from django.views.generic import RedirectView
from django.shortcuts import get_object_or_404
from django.db import IntegrityError
from django.contrib import messages
from django.urls import reverse_lazy

from gatheros_event.models import Organization


class NotAllowedOrganization(IntegrityError):
    def __init__( self, *args, **kwargs ):
        super(NotAllowedOrganization, self).__init__(*args, **kwargs)


# @TODO Refatorar para inserir dados em sessão e mudança de contexto

class OrganizationSwitch(RedirectView):
    def post( self, request, *args, **kwargs ):
        pk = request.POST.get('organization-context-pk', None)
        next_path = request.POST.get('next', reverse_lazy('gatheros_front:home'))
        if not pk:
            return

        organization = get_object_or_404(Organization, pk=pk)
        org_data = {
            'pk': organization.pk,
            'name': organization.name,
            'internal': organization.internal
        }

        # Verifica se organização está na relação de organizações
        if org_data not in request.session['organizations']:
            raise NotAllowedOrganization("Você não tem permissão para acessar esta organização.")

        # Verifica se é membro, em caso de interceptação e mudança de dados da sessão
        if org_data['pk'] not in [member['organization']['pk'] for member in request.session['members']]:
            raise NotAllowedOrganization("Você não tem permissão para acessar esta organização.")

        request.session['organization_context'] = org_data
        request.session['member_group'] = self._get_member_group(organization, request.user.person)

        if organization.internal is True:
            context = 'não está em organização'
        else:
            context = "está na organização '{}'".format(organization.name)

        messages.info(request, "Agora você {}.".format(context))

        self.url = next_path
        return super(OrganizationSwitch, self).post(request, *args, **kwargs)

    def _get_member_group( self, organization, person ):
        for member in organization.members.all():
            if member.person == person:
                return {
                    'group': member.group,
                    'group_name': member.get_group_display()
                }
