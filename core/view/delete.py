# pylint: disable=R0901
"""Gatheros view mixin for deletion of models"""

from django.contrib import messages
from django.core.exceptions import ImproperlyConfigured
from django.forms.models import model_to_dict
from django.shortcuts import redirect
from django.views.generic import DeleteView

from core.model.deletable import DeletableModel
from gatheros_event.views.mixins import AccountMixin


class DeleteViewMixin(AccountMixin, DeleteView):
    """Mixin class for delete view"""

    object = None
    protected = False
    delete_message = 'Tem certeza que deseja excluir?'
    success_message = "Registro excluído com sucesso!"
    model_protected_message = 'A entidade não pode ser excluída.'
    not_allowed_message = 'Você não pode excluir este registro.'
    template_name = 'generic/delete.html'

    def dispatch(self, request, *args, **kwargs):

        self.object = self.get_object()

        if not isinstance(self.object, DeletableModel):
            # noinspection PyProtectedMember
            raise ImproperlyConfigured(
                'O model "{}" não é instância de'' "{}"'.format(
                    self.object._meta.model_name,
                    'DeletableModel'
                )
            )

        if not self.can_delete():
            messages.warning(request, self.not_allowed_message)
            url = self.get_success_url()
            return redirect(url.format(**model_to_dict(self.object)))

        return super(DeleteViewMixin, self).dispatch(
            request,
            *args,
            **kwargs
        )

    def get_context_data(self, **kwargs):
        context = super(DeleteViewMixin, self).get_context_data(**kwargs)
        context['organization'] = self.organization
        context['go_back_path'] = self.get_success_url()

        # noinspection PyProtectedMember
        context['title'] = 'Excluir ' + self.object._meta.verbose_name

        data = model_to_dict(self.get_object())
        context['model_protected_message'] = self.model_protected_message
        context['delete_message'] = self.delete_message.format(**data)
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        messages.success(request, self.success_message)
        return super(DeleteViewMixin, self).post(request, *args, **kwargs)

    def can_delete(self):
        """Checks if user can delete model"""

        obj = self.get_object()

        # noinspection PyProtectedMember
        app_label = obj._meta.app_label
        # noinspection PyProtectedMember
        model_name = obj._meta.model_name
        full_name = "%s.%s_%s" % (app_label, 'delete', model_name)
        can_delete = self.request.user.has_perm(full_name, obj)

        return obj.is_deletable() and can_delete
