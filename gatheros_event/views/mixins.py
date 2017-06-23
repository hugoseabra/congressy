from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ImproperlyConfigured, PermissionDenied
from django.forms.models import model_to_dict
from django.shortcuts import redirect
from django.utils.functional import SimpleLazyObject
from django.views.generic import DeleteView
from django.views.generic.base import View

from core.model.deletable import DeletableModel
from gatheros_event.helpers.account import (
    get_member,
    get_organization,
    get_organizations,
    is_participant,
)


class AccountMixin(LoginRequiredMixin, View):
    permission_denied_url = '/'
    raise_exception = True  # If not logged
    permission_denied_message = 'Você não pode realizar esta ação.'

    @property
    def is_participant(self):
        return is_participant(self.request)

    @property
    def organization(self):
        return SimpleLazyObject(lambda: get_organization(self.request))

    @property
    def member(self):
        return SimpleLazyObject(lambda: get_member(self.request))

    @property
    def organizations(self):
        return SimpleLazyObject(lambda: get_organizations(self.request))

    @property
    def has_internal_organization(self):
        orgs = [org for org in self.organizations if org.internal]
        return len(orgs) == 1

    @property
    def has_organization(self):
        user = self.request.user
        orgs = [org for org in self.organizations if org.is_admin(user)]
        return len(orgs) == 1

    # noinspection PyMethodMayBeStatic
    def can_access(self):
        """ Verifica se usuário pode acessar o conteúdo da view. """
        return True

    def get_permission_denied_url(self):
        """ Resgata url quando permissão negada. """
        return self.permission_denied_url

    def dispatch(self, request, *args, **kwargs):
        try:
            if not self.can_access():
                raise PermissionDenied(self.get_permission_denied_message())

            return super(AccountMixin, self).dispatch(
                request,
                *args,
                **kwargs
            )

        except PermissionDenied as e:
            messages.warning(request, e)
            return redirect(self.get_permission_denied_url())


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
        try:
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
                raise PermissionDenied(self.not_allowed_message)

            return super(DeleteViewMixin, self).dispatch(
                request,
                *args,
                **kwargs
            )

        except PermissionDenied as e:
            messages.warning(request, e)
            return redirect(self.get_permission_denied_url())

    def get_permission_denied_url(self):
        url = self.get_success_url()
        return url.format(**model_to_dict(self.object))

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

        self.pre_delete()
        messages.success(request, self.success_message)
        response = super(DeleteViewMixin, self).post(request, *args, **kwargs)
        self.post_delete()
        return response

    def can_delete(self):
        """Checks if user can delete model"""

        if not self.can_access():
            return False

        obj = self.get_object()

        # noinspection PyProtectedMember
        app_label = obj._meta.app_label
        # noinspection PyProtectedMember
        model_name = obj._meta.model_name
        full_name = "%s.%s_%s" % (app_label, 'delete', model_name)
        can_delete = self.request.user.has_perm(full_name, obj)

        return obj.is_deletable() and can_delete

    # noinspection PyMethodMayBeStatic
    def pre_delete(self):
        """ Processo a ser executado antes de deletar. """
        pass

    def post_delete(self):
        """ Processo a ser executado depois de deletar. """
        pass
