from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views import generic

from gatheros_event.models import Event
from gatheros_event.views.mixins import AccountMixin
from gatheros_subscription.forms import (
    EventFieldsForm,
    FormFieldForm,
    FormFieldOrderForm,
)
from gatheros_subscription.models import Field


class BaseEventViewMixin(AccountMixin, generic.View):
    """ Base de View para resgatar informações de evento. """
    event = None

    def get_permission_denied_url(self):
        """ URL de redirecionamento caso a permissão seja negada. """
        return reverse('event:event-panel', kwargs={
            'pk': self.kwargs.get('event_pk')
        })

    def _get_event(self):
        if not self.event:
            pk = self.kwargs.get('event_pk')
            self.event = get_object_or_404(Event, pk=pk)

        return self.event

    def can_access(self):
        """ Verifica se usuário pode acessar o conteúdo da view. """
        event = self._get_event()
        org = self.organization
        same_org = org and event.organization.pk == org.pk
        enabled = event.subscription_type != event.SUBSCRIPTION_DISABLED
        can_view = self.request.user.has_perm(
            'gatheros_subscription.change_form',
            event.form
        ) if enabled else False

        return same_org and enabled and can_view


class BaseFormFieldView(BaseEventViewMixin, generic.TemplateView):
    """ Classe base para view de formulários. """
    form_title = 'Formulário'

    def get_context_data(self, **kwargs):
        """ Recupera contexto da view. """
        context = super(BaseFormFieldView, self).get_context_data(**kwargs)
        context.update({
            'event': self._get_event(),
            'form_title': self.get_form_title(),
        })
        return context

    def get_form_title(self):
        return self.form_title


class EventConfigFormFieldView(BaseFormFieldView, generic.FormView):
    """ View para exibição de lista de campos do formulário de evento. """
    form_class = EventFieldsForm
    template_name = 'gatheros_subscription/event_form/config.html'
    form_title = 'Configuração de Formulário'

    def get_context_data(self, **kwargs):
        """ Recupera contexto da view. """
        cxt = super(EventConfigFormFieldView, self).get_context_data(**kwargs)
        form = cxt['form']
        fields_dict = form.gatheros_fields

        default_fields = []
        additional_fields = []
        for form_field in cxt['form']:
            field = fields_dict.get(form_field.name)
            if field.form_default_field:
                default_fields.append({
                    'form_field': form_field,
                    'field': field
                })
            else:
                additional_fields.append({
                    'form_field': form_field,
                    'field': field
                })

        cxt.update({
            'default_fields': default_fields,
            'additional_fields': additional_fields,
        })
        return cxt

    # noinspection PyUnresolvedReferences
    def get_form_kwargs(self):
        """ Recupera atributos de início do formulário. """
        event = self._get_event()
        kwargs = super(EventConfigFormFieldView, self).get_form_kwargs()
        kwargs.update({
            'form': event.form,
            'show_inactive': True
        })
        return kwargs


class EventFormFieldAddView(BaseFormFieldView, generic.CreateView):
    form_title = 'Adicionar Campo de Formulário'
    success_message = 'Campo criado com sucesso.'

    def get_success_url(self):
        """ Recupera URL de redirecionamento em caso de sucesso. """
        pass
        # return reverse(
        #     'subscription:event-fields-config',
        #     kwargs={'event_pk': self.kwargs['event_pk']}
        # )

    def can_access(self):
        """ Verifica se usuário pode acessar o conteúdo da view. """
        can_access = super(EventFormFieldAddView, self).can_access()
        event = self._get_event()
        can_add = self.request.user.has_perm(
            'gatheros_subscription.can_add_field',
            event.form
        )
        return can_access and can_add


class EventFormFieldRemoveView(BaseEventViewMixin):
    """ View para remover relação entre Formulário e Campo de formulário. """
    http_method_names = ['post']
    field = None

    def pre_dispatch(self, request):
        """ Operações executadas antes do dispatch de uma view. """
        self.field = get_object_or_404(Field, pk=self.kwargs.get('pk'))
        super(EventFormFieldRemoveView, self).pre_dispatch(request)

    def get_success_url(self):
        """ Recupera URL de redirecionamento em caso de sucesso. """
        return reverse(
            'subscription:event-fields-config',
            kwargs={'event_pk': self.kwargs['event_pk']}
        )

    # noinspection PyUnusedLocal
    def post(self, request, *args, **kwargs):
        """ request method POST """
        event = self._get_event()
        form = event.form

        form.fields.remove(self.field)
        form.save()

        return redirect(self.get_success_url())


class EventFormFieldReorderView(BaseEventViewMixin):
    """ View para reordenação de campo no formulário. """
    http_method_names = ['post']
    order_form = None
    form = None
    field = None

    def pre_dispatch(self, request):
        """ Operações executadas antes do dispatch de uma view. """
        event = self._get_event()
        self.form = FormFieldOrderForm(form=event.form)
        self.field = get_object_or_404(Field, pk=self.kwargs.get('pk'))
        super(EventFormFieldReorderView, self).pre_dispatch(request)

    # noinspection PyUnusedLocal
    def post(self, request, *args, **kwargs):
        """ request method POST """
        try:
            event = self._get_event()

            success = False

            if request.POST.get('up') is not None:
                success = True
                self.form.order_up(self.field)

            if request.POST.get('down') is not None:
                success = True
                self.form.order_down(self.field)

            if not success:
                raise Exception('Envie o campo `order` como `up` ou `down`')

        except Exception as e:
            messages.error(request, 'Algum erro ocorreu: ' + str(e))

        finally:
            return redirect(reverse(
                'subscription:event-fields-config',
                kwargs={'event_pk': self.kwargs['event_pk']}
            ))

    def can_access(self):
        """ Verifica se usuário pode acessar o conteúdo da view. """
        can_access = super(EventFormFieldReorderView, self).can_access()
        not_default = self.field.form_default_field is False
        can_change = self.request.user.has_perm(
            'gatheros_subscription.change_field',
            self.field
        ) if not_default else False

        return can_access and can_change


class EventFormFieldManageActivationView(BaseEventViewMixin):
    """ View para gerenciar ativação/desativação de campo no formulário. """
    http_method_names = ['post']
    order_form = None
    form = None
    field = None

    def pre_dispatch(self, request):
        """ Operações executadas antes do dispatch de uma view. """
        event = self._get_event()
        self.form = FormFieldForm(form=event.form)
        self.field = get_object_or_404(Field, pk=self.kwargs.get('pk'))
        super(EventFormFieldManageActivationView, self).pre_dispatch(request)

    # noinspection PyUnusedLocal
    def post(self, request, *args, **kwargs):
        """ request method POST """
        try:
            event = self._get_event()
            success = False
            action = request.POST.get('action')

            if action == 'activate':
                success = True
                self.form.activate(self.field)

            if action == 'deactivate':
                success = True
                self.form.deactivate(self.field)

            if not success:
                raise Exception(
                    'Envie o campo `action` como `activate` ou `deactivate`'
                )

        except Exception as e:
            messages.error(request, 'Algum erro ocorreu: ' + str(e))

        finally:
            return redirect(reverse(
                'subscription:event-fields-config',
                kwargs={'event_pk': self.kwargs['event_pk']}
            ))

    def can_access(self):
        """ Verifica se usuário pode acessar o conteúdo da view. """
        parent = super(EventFormFieldManageActivationView, self)
        can_access = parent.can_access()
        not_default = self.field.form_default_field is False
        return can_access and not_default


class EventFormFieldManageRequirementView(BaseEventViewMixin):
    """
    View para gerenciar campos obrigatórios e não-obrigatórios no formulário.
    """
    http_method_names = ['post']
    order_form = None
    form = None
    field = None

    def pre_dispatch(self, request):
        """ Operações executadas antes do dispatch de uma view. """
        event = self._get_event()
        self.form = FormFieldForm(form=event.form)
        self.field = get_object_or_404(Field, pk=self.kwargs.get('pk'))
        super(EventFormFieldManageRequirementView, self).pre_dispatch(request)

    # noinspection PyUnusedLocal
    def post(self, request, *args, **kwargs):
        """ request method POST """
        try:
            event = self._get_event()
            success = False
            action = request.POST.get('action')

            if action == 'required':
                success = True
                self.form.set_as_required(self.field)

            if action == 'not-required':
                success = True
                self.form.set_as_not_required(self.field)

            if not success:
                raise Exception(
                    'Envie o campo `action` como `required` ou `not-required`'
                )

        except Exception as e:
            messages.error(request, 'Algum erro ocorreu: ' + str(e))

        finally:
            return redirect(reverse(
                'subscription:event-fields-config',
                kwargs={'event_pk': self.kwargs.get('event_pk')}
            ))
