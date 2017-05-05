# from django.http import Http404
from django.urls import reverse_lazy, reverse

from gatheros_event.lib.view.organization_permission import OrganizationPermissionViewMixin
from gatheros_event.lib.view.delete import DeleteViewMixin
from gatheros_event.models import Event, Member
from django.contrib import messages
from django.shortcuts import redirect


class EventDeleteView(DeleteViewMixin, OrganizationPermissionViewMixin):
    model = Event
    template_name = 'gatheros_event/event/event_confirm_delete.html'
    success_url = reverse_lazy('gatheros_event:event-list')
    delete_message = "Não é possível excluir o evento '{name}' possivelmente porque há lotes com inscrições." \
                     " Exporte, gerencie e exclua os lotes antes de excluir este evento."

    def dispatch( self, request, *args, **kwargs ):
        self.check(request)
        return super(EventDeleteView, self).dispatch(request, *args, **kwargs)

    def render_to_response( self, context, **response_kwargs ):
        # if not self.can_delete():
            # messages.success(self.request, "Você não tem permissão para excluir este evento")
            # return redirect(self.success_url.format(**self.object.__dict__))

        return super(EventDeleteView, self).render_to_response(context=context, **response_kwargs)

    def post(self, request, *args, **kwargs):
        if not self.can_delete():
            messages.success(self.request, "Você não tem permissão para excluir este evento")
            return redirect(self.success_url.format(**self.object.__dict__))

        return super(EventDeleteView, self).post(request, *args, **kwargs)

    def can_delete( self ):
        if self.super_user:
            return True

        self.object = self.get_object()

        return self.object.organization.pk == self.organization['pk'] or self.member_group['group'] == Member.ADMIN
