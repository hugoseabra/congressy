from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.views.generic import DeleteView

from gatheros_event.views.mixins import AccountMixin


class DeleteViewMixin(AccountMixin, DeleteView):
    protected = False
    message = 'Você está prestes a excluir este registro. Deseja realmente' \
              ' continuar?'
    delete_message = 'Tem certeza que deseja excluir?'
    success_message = "Registro excluído com sucesso!"
    not_allowed_message = 'Você não tem permissão para excluir este registro.'

    def render_to_response(self, context, **response_kwargs):
        if not self.can_delete():
            messages.warning(self.request, self.not_allowed_message)
            return redirect(self.success_url.format(**self.object.__dict__))

        return super(DeleteViewMixin, self).render_to_response(
            context=context,
            **response_kwargs
        )

    def get_context_data(self, **kwargs):
        context = super(DeleteViewMixin, self).get_context_data(**kwargs)
        context['protected'] = self.protected

        data = self.object.__dict__
        context['delete_message'] = self.delete_message.format(**data)
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        if self.can_delete() is False:
            raise PermissionDenied('Você não pode excluir este registro.')

        messages.success(request, self.success_message)
        return super(DeleteViewMixin, self).post(request, *args, **kwargs)

    def can_delete(self):
        obj = self.get_object()

        app_label = obj._meta.app_label
        model_name = obj._meta.model_name
        full_name = "%s.%s_%s" % (app_label, 'delete', model_name)
        can_delete = self.request.user.has_perm(full_name, self.get_object())

        return obj.is_deletable() and can_delete

