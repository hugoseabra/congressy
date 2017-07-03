from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ImproperlyConfigured, PermissionDenied
from django.forms.models import model_to_dict
from django.shortcuts import redirect
from django.utils.functional import SimpleLazyObject
from django.views.generic import DeleteView
from django.views.generic.base import View

from core.model.deletable import DeletableModelMixin
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
    def is_authenticated(self):
        """ Verifica se há autenticação de usuário. """
        user = self.request.user if hasattr(self.request, 'user') else None
        return user.is_authenticated() if user else False

    @property
    def is_participant(self):
        """ Verifica se usuário é participante apenas. """
        return is_participant(self.request)

    @property
    def organization(self):
        """ Resgata objeto Organization do contexto do usuário. """
        return SimpleLazyObject(lambda: get_organization(self.request))

    @property
    def member(self):
        """ Resgata objeto Member do usuário logado. """
        return SimpleLazyObject(lambda: get_member(self.request))

    @property
    def organizations(self):
        """
        Resgata um objeto contendo uma lista de Organization do usuário.
        """
        return SimpleLazyObject(lambda: get_organizations(self.request))

    @property
    def has_internal_organization(self):
        """ Verifica se usuário possui organização interna. """
        orgs = [org for org in self.organizations if org.internal]
        return len(orgs) == 1

    @property
    def has_organization(self):
        """ Verifica se o usuário logado está em alguma organização. """
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

    def pre_dispatch(self, request):
        if not self.is_authenticated:
            raise PermissionDenied(self.get_permission_denied_message())

        if not self.can_access():
            raise PermissionDenied(self.get_permission_denied_message())

    def dispatch(self, request, *args, **kwargs):
        """ Dispatch padrão da view. """
        try:
            self.pre_dispatch(request)

            dispatch = super(AccountMixin, self).dispatch(
                request,
                *args,
                **kwargs
            )
        except PermissionDenied as e:
            messages.warning(request, str(e))
            return redirect(self.get_permission_denied_url())

        else:
            return dispatch


class DeleteViewMixin(AccountMixin, DeleteView):
    """Mixin class for delete view"""

    object = None
    protected = False
    delete_message = 'Tem certeza que deseja excluir?'
    success_message = "Registro excluído com sucesso!"
    model_protected_message = 'A entidade não pode ser excluída.'
    not_allowed_message = 'Você não pode excluir este registro.'
    template_name = 'generic/delete.html'

    def get_object(self, queryset=None):
        if not self.object:
            self.object = super(DeleteViewMixin, self).get_object(queryset)

        return self.object

    def pre_dispatch(self, request):
        super(DeleteViewMixin, self).pre_dispatch(request)

        self.object = self.get_object()

        if not isinstance(self.object, DeletableModelMixin):
            # noinspection PyProtectedMember
            model_name = self.object._meta.model_name
            module_path = DeletableModelMixin.__module__
            raise ImproperlyConfigured(
                'O model "{}" não é instância de "{}"'.format(
                    model_name,
                    module_path + '.DeletableModelMixin'
                )
            )

        if not self.can_delete():
            raise PermissionDenied(self.not_allowed_message)

    def get_permission_denied_url(self):
        url = self.get_success_url()
        return url.format(**model_to_dict(self.object)) if self.object else url

    def get_context_data(self, **kwargs):
        context = super(DeleteViewMixin, self).get_context_data(**kwargs)
        context['organization'] = self.organization
        context['go_back_path'] = self.get_success_url()

        # noinspection PyProtectedMember
        verbose_name = self.object._meta.verbose_name
        context['title'] = 'Excluir {}'.format(verbose_name)

        data = model_to_dict(self.get_object())
        context['delete_message'] = self.delete_message.format(**data)
        return context

    def post(self, request, *args, **kwargs):
        try:
            self.pre_delete()

            response = super(DeleteViewMixin, self).post(
                request,
                *args,
                **kwargs
            )

        except Exception as e:
            messages.error(request, str(e))
            return redirect(self.get_success_url())

        else:
            messages.success(request, self.success_message)
            self.post_delete()
            return response

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

    # noinspection PyMethodMayBeStatic
    def pre_delete(self):
        """ Processo a ser executado antes de deletar. """
        pass

    def post_delete(self):
        """ Processo a ser executado depois de deletar. """
        pass
