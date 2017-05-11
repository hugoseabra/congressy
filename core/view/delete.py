from django.contrib import messages
from django.shortcuts import redirect
from django.views.generic import DeleteView

from core.model.deletable import NotDeletableError
from core.view.user_context import UserContextViewMixin


class DeleteViewMixin(UserContextViewMixin, DeleteView):
    protected = False
    message = None
    delete_message = 'Tem certeza que deseja excluir?'
    success_message = "Registro excluído com sucesso!"
    not_allowed_message = 'Você não tem permissão para excluir este registro.'

    def render_to_response(self, context, **response_kwargs):
        if self._not_allowed():
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

    def get_object(self, queryset=None):
        obj = super(DeleteViewMixin, self).get_object(queryset=queryset)

        try:
            obj.check_deletable()
        except NotDeletableError:
            self.protected = True

        return obj

    def post(self, request, *args, **kwargs):
        if self._not_allowed():
            messages.warning(self.request, self.not_allowed_message)
            return redirect(self.success_url.format(**self.object.__dict__))

        messages.success(request, self.success_message)
        return super(DeleteViewMixin, self).post(request, *args, **kwargs)

    def can_delete(self):
        raise NotImplementedError('`can_delete()` deve ser implementado.')

    def _not_allowed(self):
        return self.request.user.is_superuser \
               and self.can_delete() is False
