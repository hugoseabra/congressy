# from django.http import Http404
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy

from core.view.delete import DeleteViewMixin
from core.view.user_context import UserContextMixin
from gatheros_event.models import Event, Member


class EventDeleteView(LoginRequiredMixin, UserContextMixin, DeleteViewMixin):
    model = Event
    template_name = 'gatheros_event/event/event_confirm_delete.html'
    success_url = reverse_lazy('gatheros_event:event-list')
    delete_message = "Não é possível excluir o evento '{name}' possivelmente porque há lotes com inscrições." \
                     " Exporte, gerencie e exclua os lotes antes de excluir este evento."

    def render_to_response( self, context, **response_kwargs ):
        if not self.can_delete():
            messages.success(self.request, "Você não tem permissão para excluir este evento")
            return redirect(self.success_url.format(**self.object.__dict__))

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
