""" Mixins de views. """
from datetime import datetime

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import ImproperlyConfigured, PermissionDenied
from django.forms.models import model_to_dict
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils.functional import SimpleLazyObject
from django.utils.translation import ugettext as _
from django.views import generic
from django.views.generic import DeleteView
from django.views.generic.base import View
from django.views.generic.edit import FormMixin
from django.views.generic.list import ListView

from core.model.deletable import DeletableModelMixin
from gatheros_event.helpers.account import get_member, get_organization, \
    get_organizations, is_manager, update_account
from gatheros_event.helpers.event_business import is_paid_event
from gatheros_event.helpers.publishing import event_is_publishable
from gatheros_event.models import Event, Member


class AccountMixin(LoginRequiredMixin, View):
    """ Mixin para gerenciamento de contexto de conta de usuário na view. """
    permission_denied_url = '/'
    raise_exception = True  # If not logged
    permission_denied_message = 'Você não pode realizar esta ação.'

    @property
    def is_authenticated(self):
        """ Verifica se há autenticação de usuário. """
        user = self.request.user if hasattr(self.request, 'user') else None
        return user.is_authenticated() if user else False

    @property
    def is_manager(self):
        """ Verifica se usuário é participante apenas. """
        return is_manager(self.request)

    @property
    def organization(self):
        """ Resgata objeto Organization do contexto do usuário. """
        return SimpleLazyObject(lambda: get_organization(self.request))

    @property
    def organizaton_only_admin(self):
        """ Verifica se o membro é o único administrador da organização. """
        if self.organization.internal:
            return True

        admins = self.organization.get_members(group=Member.ADMIN).count()
        return admins == 1

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
    def is_organization_admin(self):
        """ Verifica se usuário é ADMIN de alguma organização. """
        user = self.request.user
        orgs = [org for org in self.organizations if org.is_admin(user)]
        return len(orgs) > 0

    # noinspection PyMethodMayBeStatic
    def can_access(self):
        """ Verifica se usuário pode acessar o conteúdo da view. """
        return True

    def get_permission_denied_url(self):
        """ Resgata url quando permissão negada. """
        return self.permission_denied_url

    def pre_dispatch(self, request):
        """ Operações executadas antes do dispatch de uma view. """
        if not self.can_access():
            raise PermissionDenied(self.get_permission_denied_message())

    def dispatch(self, request, *args, **kwargs):
        """ Dispatch padrão da view. """
        try:
            if not self.is_authenticated:
                return redirect_to_login(
                    self.request.get_full_path(),
                    self.get_login_url(),
                    self.get_redirect_field_name()
                )

            self.pre_dispatch(request)

            dispatch = super(AccountMixin, self).dispatch(
                request,
                *args,
                **kwargs
            )

        except PermissionDenied as e:
            messages.warning(request, str(e))
            # @TODO Delete an event is not working, not catching permission denied.
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
        """ Resgata objeto principal da view. """
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
        delete_message = self.get_delete_message()
        context['delete_message'] = delete_message.format(**data)
        return context

    def get_delete_message(self):
        """
        Recupera mensagem de remoção a ser perguntada ao usuário antes da
        remoção.
        """
        return self.delete_message

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

    # noinspection PyMethodMayBeStatic
    def post_delete(self):
        """ Processo a ser executado depois de deletar. """
        pass


class FormListViewMixin(FormMixin, ListView):
    """ Lista com formulário """
    object_list = None
    form = None

    def get_form_kwargs(self):
        """
        Retorna argumentos para inicializar o form

        :return: dict
        """
        kwargs = super(FormListViewMixin, self).get_form_kwargs()

        if self.request.method == 'GET':
            kwargs.update({
                'data': self.request.GET,
            })

        return kwargs

    def get(self, request, *args, **kwargs):
        """
        Processa o metodo get, devolvendo o form a lista e renderizando o
        template

        :param request:
        :param args:
        :param kwargs:
        :return: Response
        """
        # From ProcessFormMixin
        form_class = self.get_form_class()
        self.form = self.get_form(form_class)

        # From BaseListView
        self.object_list = self.get_queryset()
        allow_empty = self.get_allow_empty()
        if not allow_empty and len(self.object_list) == 0:
            raise Http404(
                _(u"Empty list and '%(class_name)s.allow_empty' is False.")
                % {'class_name': self.__class__.__name__})

        context = self.get_context_data(object_list=self.object_list,
                                        form=self.form)
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)


class EventViewMixin(AccountMixin):
    """ Mixin de view para vincular com informações de event. """

    def __init__(self, *args, **kwargs):
        self.event = None
        super().__init__(*args, **kwargs)

    def dispatch(self, request, *args, **kwargs):
        event = self.get_event()

        update_account(
            request=self.request,
            organization=event.organization,
            force=True
        )

        self.permission_denied_url = reverse(
            'event:event-panel',
            kwargs={'pk': self.kwargs.get('event_pk')}
        )
        return super(EventViewMixin, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        # noinspection PyUnresolvedReferences
        context = super(EventViewMixin, self).get_context_data(**kwargs)
        is_payable = is_paid_event(self.event)
        context['event'] = self.get_event()
        context['is_paid_event'] = is_paid_event(self.event)
        context['event_is_payable'] = is_payable

        return context

    def get_event(self):
        """ Resgata organização do contexto da view. """

        if self.event:
            return self.event

        self.event = get_object_or_404(
            Event,
            pk=self.kwargs.get('event_pk')
        )
        return self.event

    def can_access(self):
        return self.get_event().organization == self.organization

    def get_permission_denied_url(self):
        return reverse('event:event-list')


class EventDraftStateMixin(object):

    def get_context_data(self, **kwargs):

        if 'view' not in kwargs:
            kwargs['view'] = self

        context = kwargs

        event = kwargs.get('event')
        if not event:
            return context

        context['selected_event'] = event
        context['is_event_publishable'] = event_is_publishable(event)

        return context


class MultiLotsFeatureFlagMixin(AccountMixin, generic.View):
    event = None
    permission_denied_message = 'Você não pode realizar esta ação.'

    def get_permission_denied_url(self):
        return reverse(
            'event:event-panel',
            kwargs={
                'pk': self.event.pk,
            }
        )

    def pre_dispatch(self, request):
        self.event = get_object_or_404(
            Event,
            pk=self.kwargs.get('event_pk'),
        )

        response = super().pre_dispatch(request)
        features = self.event.feature_configuration

        if features.feature_multi_lots is False:
            raise PermissionDenied(self.get_permission_denied_message())
        return response
