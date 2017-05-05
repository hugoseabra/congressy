from django.contrib import messages
from django.db import IntegrityError
from django.urls import reverse_lazy
from django.views.generic import RedirectView

from gatheros_event.acl.gatheros_user_context import update_user_context


class NotAllowedOrganization(IntegrityError):
    def __init__( self, *args, **kwargs ):
        super(NotAllowedOrganization, self).__init__(*args, **kwargs)


# @TODO Refatorar para inserir dados em sessão e mudança de contexto

class OrganizationSwitch(RedirectView):
    def post( self, request, *args, **kwargs ):
        pk = request.POST.get('organization-context-pk', None)
        next_path = request.POST.get('next',
                                     reverse_lazy('gatheros_front:home'))
        if not pk:
            return

        user_context = update_user_context(request, pk)
        organization = user_context.organization

        if organization.internal is True:
            context = 'não está em organização'
        else:
            context = "está na organização '{}'".format(organization.name)

        messages.info(request, "Agora você {}.".format(context))

        self.url = next_path
        return super(OrganizationSwitch, self).post(request, *args, **kwargs)
