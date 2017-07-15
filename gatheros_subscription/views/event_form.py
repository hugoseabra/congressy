""" Views de formulário de evento. """
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views import generic

from gatheros_event.models import Event
from gatheros_event.views.mixins import AccountMixin
from gatheros_subscription.forms import (
    FieldForm,
    EventFieldsForm,
    FormFieldForm,
    FormFieldOrderForm,
)
from gatheros_subscription.models import Field


class BaseEventViewMixin(AccountMixin, generic.TemplateView):
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

    def get_context_data(self, **kwargs):
        """ Recupera contexto da view. """
        context = super(BaseEventViewMixin, self).get_context_data(**kwargs)
        context.update({'event': self._get_event()})
        return context

    def can_access(self):
        """ Verifica se usuário pode acessar o conteúdo da view. """
        if not self.is_manager:
            return False

        event = self._get_event()
        org = self.organization
        same_org = org and event.organization.pk == org.pk
        enabled = event.subscription_type != event.SUBSCRIPTION_DISABLED
        can_view = self.request.user.has_perm(
            'gatheros_subscription.change_form',
            event.form
        ) if enabled else False

        return same_org and enabled and can_view


class BaseFormFieldView(BaseEventViewMixin):
    """ Classe base para view de formulários. """
    form_title = 'Formulário'

    def get_context_data(self, **kwargs):
        """ Recupera contexto da view. """
        context = super(BaseFormFieldView, self).get_context_data(**kwargs)
        context.update({'form_title': self.get_form_title()})
        return context

    def get_form_title(self):
        """ Resgata título do formulário. """
        return self.form_title


class EventConfigFormFieldView(BaseFormFieldView, generic.FormView):
    """ View para exibição de lista de campos do formulário de evento. """
    form_class = EventFieldsForm
    template_name = 'gatheros_subscription/form/config.html'
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


class EventFormFieldAddView(BaseFormFieldView, generic.TemplateView):
    """ View para adicionar campos ao formulário. """

    template_name = 'gatheros_subscription/form/field_add.html'
    success_message = 'Campo criado com sucesso.'

    def get_field_form(self):
        """ Resgata instância de formulário de campo. """
        event = self._get_event()
        return FieldForm(organization=event.organization)

    def get_context_data(self, **kwargs):
        """ Recupera contexto da view. """
        context = super(BaseFormFieldView, self).get_context_data(**kwargs)

        action = self.request.GET.get('action')
        context.update({'action': action})

        event = self._get_event()
        organization = event.organization

        event_field_pks = [field.pk for field in event.form.fields.all()]

        org_fields_qs = organization.fields.exclude(pk__in=event_field_pks)
        org_fields_qs = org_fields_qs.filter(
            active=True,
            form_default_field=False
        )
        org_fields_qs = org_fields_qs.order_by('-required',  'label')

        events_qs = organization.events.exclude(
            Q(form__isnull=True) | Q(pk=event.pk)
        )

        events = [
            ev for ev in events_qs
            if len(ev.form.fields.exclude(pk__in=event_field_pks))
        ]

        context.update({
            'form_title': 'Adicionar campo',
            'org_fields': org_fields_qs,
            'events': events
        })

        def not_allowed(extra_msg=None):
            """ Envia exceção de permissão negada. """
            msg = 'Você não pode inserir este campo'
            if extra_msg:
                msg += ': ' + extra_msg

            msg += '.'
            raise PermissionDenied(msg)

        def select_event(ev_pk):
            """ Resgata instância de evento. """
            try:
                # noinspection PyShadowingNames
                event = Event.objects.exclude(form__isnull=True).get(pk=ev_pk)

            except Event.DoesNotExist as e:
                not_allowed(str(e))

            else:
                if event.organization.pk != organization.pk:
                    not_allowed()

                return event

        def select_field(field_pk):
            """ Resgata instância de `Field`"""
            try:
                field = Field.objects.exclude(
                    form_default_field=True
                ).get(pk=field_pk)

            except Field.DoesNotExist as e:
                not_allowed(str(e))

            else:
                if field.organization.pk != organization.pk:
                    not_allowed()

                return field

        def select_event_fields(ev):
            """" Resgata campos de `Event` """
            return ev.form.fields.exclude(
                Q(pk__in=event_field_pks) |
                Q(form_default_field=True) |
                Q(active=False)
            ).order_by('-required',  'label')

        if action == 'field':
            selected_field = select_field(self.request.GET.get('field'))
            context.update({
                'form_title': 'Adicionar campo padrão',
                'selected_field': selected_field
            })

        if action == 'copy':
            selected_event = select_event(self.request.GET.get('from'))
            selected_event_fields = select_event_fields(selected_event)

            if selected_event_fields.count() == 0:
                not_allowed()

            context.update({
                'form_title': 'Copiar formulário',
                'selected_event': selected_event,
                'selected_event_fields': selected_event_fields,
            })

        if action == 'add':
            context.update({'form': self.get_field_form()})

        return context

    # noinspection PyUnusedLocal
    def post(self, request, *args, **kwargs):
        """ request method POST """
        event = self._get_event()
        form = FormFieldForm(form=event.form)

        try:
            action = request.POST.get('action')

            success = False
            if action == 'add':
                form.add_new_field(request.POST)
                messages.success(request, 'Campo adicionado com sucesso.')
                success = True

            elif action == 'add_existing':
                field_name = request.POST.get('field_name')
                requirement = request.POST.get('requirement')

                if not field_name:
                    raise Exception('Nenhum campo encontrado.')

                if requirement == 'required':
                    is_required = True

                elif requirement == 'not-required':
                    is_required = False

                else:
                    is_required = None

                form.add_field(field_name, is_required)

                messages.success(request, 'Campo adicionado com sucesso.')
                success = True

            elif action == 'copy':
                fields_list = request.POST.getlist('fields_list')
                requirement_list = request.POST.getlist('requirement_list')

                if not fields_list:
                    raise Exception('Nenhum campo foi enviado.')

                fields_dict = {}
                for idx, field_name in enumerate(fields_list):
                    is_required = None
                    try:
                        requirement = requirement_list[idx]
                        if requirement == 'required':
                            is_required = True

                        elif requirement == 'not-required':
                            is_required = False

                        else:
                            is_required = None

                    except IndexError:
                        is_required = None

                    fields_dict.update({field_name: is_required})

                form.add_fields_by_names(fields_dict)

                messages.success(request, 'Campos adicionados com sucesso.')
                success = True

            if not success:
                raise Exception(
                    'Ação inválida. Envie `copy`, `add` ou `add_existing`.'
                )

        except Exception as e:
            messages.error(request, 'Algum erro ocorreu: ' + str(e))
            return self.render_to_response(self.get_context_data())

        else:
            return redirect(self.get_success_url())

    def get_success_url(self):
        """ Recupera URL de redirecionamento em caso de sucesso. """
        return reverse(
            'subscription:event-fields-config',
            kwargs={'event_pk': self.kwargs['event_pk']}
        )

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
