from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views import generic

from gatheros_event.models import Event
from gatheros_event.views.mixins import AccountMixin, DeleteViewMixin
from gatheros_subscription.forms import (
    EventConfigForm,
    EventFormFieldForm,
    EventFormFieldOrderForm,
)
from gatheros_subscription.models import Field


class BaseFormFieldView(AccountMixin, generic.TemplateView):
    form_title = 'Formulário'
    event = None

    def get_permission_denied_url(self):
        return reverse('gatheros_event:event-panel', kwargs={
            'pk': self.kwargs.get('event_pk')
        })

    def get_context_data(self, **kwargs):
        context = super(BaseFormFieldView, self).get_context_data(**kwargs)
        context.update({
            'event': self._get_event(),
            'form_title': self.get_form_title(),
        })
        return context

    def get_form_title(self):
        return self.form_title

    def _get_event(self):
        if not self.event:
            pk = self.kwargs.get('event_pk')
            self.event = get_object_or_404(Event, pk=pk)

        return self.event

    def can_access(self):
        event = self._get_event()
        org = self.organization
        same_org = org and event.organization.pk == org.pk
        enabled = event.subscription_type != event.SUBSCRIPTION_DISABLED
        can_view = self.request.user.has_perm(
            'gatheros_subscription.change_form',
            event.form
        ) if enabled else False

        return same_org and enabled and can_view


class BaseEventFormFieldForm(BaseFormFieldView):
    form_class = EventFormFieldForm
    model = form_class.Meta.model
    template_name = 'gatheros_subscription/event_form/form.html'
    success_message = None
    pk_url_kwarg = 'field_pk'
    object = None

    def get_form(self, form_class=None):
        if not form_class:
            form_class = self.form_class

        event = self._get_event()
        # noinspection PyUnresolvedReferences
        return form_class(form=event.form, **self.get_form_kwargs())

    def form_valid(self, form):
        messages.success(self.request, self.success_message)
        # noinspection PyUnresolvedReferences
        return super(BaseEventFormFieldForm, self).form_valid(form)

    def get_success_url(self):
        return reverse(
            'gatheros_subscription:fields-config',
            kwargs={'event_pk': self.kwargs['event_pk']}
        )


class EventConfigFormFieldView(BaseFormFieldView, generic.FormView):
    form_class = EventConfigForm
    template_name = 'gatheros_subscription/event_form/config.html'
    form_title = 'Configuração de Formulário'

    def get_context_data(self, **kwargs):
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

    def get_form(self, form_class=None):
        if not form_class:
            form_class = self.form_class

        event = self._get_event()
        return form_class(
            form=event.form,
            include_inactive=True,
            **self.get_form_kwargs()
        )


class EventFormFieldAddView(BaseEventFormFieldForm, generic.CreateView):
    form_title = 'Adicionar Campo de Formulário'
    success_message = 'Campo criado com sucesso.'

    def get_success_url(self):
        return reverse(
            'gatheros_subscription:fields-config',
            kwargs={'event_pk': self.kwargs['event_pk']}
        )

    def can_access(self):
        can_access = super(EventFormFieldAddView, self).can_access()
        event = self._get_event()
        can_add = self.request.user.has_perm(
            'gatheros_subscription.can_add_field',
            event.form
        )
        return can_access and can_add


class EventFormFieldEditView(BaseEventFormFieldForm, generic.UpdateView):
    form_title = 'Editar Campo de Formulário'
    success_message = 'Campo alterado com sucesso.'

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()

        return super(EventFormFieldEditView, self).dispatch(
            request,
            *args,
            **kwargs
        )

    def can_access(self):
        can_access = super(EventFormFieldEditView, self).can_access()
        event = self._get_event()
        form = event.form
        field = self.get_object()
        same_form = field.form.pk == form.pk
        can_change = self.request.user.has_perm(
            'gatheros_subscription.change_field',
            field
        )

        return can_access and same_form and can_change


class EventFormFieldDeleteView(DeleteViewMixin, BaseFormFieldView):
    model = Field
    delete_message = "Tem certeza que deseja excluir o campo \"{label}\"?"
    success_message = "Campo excluído com sucesso!"
    pk_url_kwarg = 'field_pk'

    def get_success_url(self):
        return reverse(
            'gatheros_subscription:fields-config',
            kwargs={'event_pk': self.kwargs['event_pk']}
        )

    def post_delete(self):
        event = self._get_event()
        form = event.form

        # Reordena campos após deleção.
        counter = 1
        for field in form.fields.all():
            field.order = counter
            field.save()
            counter += 1

    def can_delete(self):
        can_delete = super(EventFormFieldDeleteView, self).can_delete()
        not_default = self.object.form_default_field is False
        return can_delete and not_default


class EventFormFieldReorderView(BaseFormFieldView):
    http_method_names = ['post']
    object = None

    def dispatch(self, request, *args, **kwargs):
        pk = self.kwargs.get('field_pk')
        self.object = get_object_or_404(Field, pk=pk)

        return super(EventFormFieldReorderView, self).dispatch(
            request,
            *args,
            **kwargs
        )

    # noinspection PyUnusedLocal
    def post(self, request, *args, **kwargs):
        try:
            form = EventFormFieldOrderForm(instance=self.object)

            success = False

            if request.POST.get('up') is not None:
                success = True
                form.order_up()

            if request.POST.get('down') is not None:
                success = True
                form.order_down()

            if not success:
                raise Exception('Envie o campo `order` como `up` ou `down`')

        except Exception as e:
            messages.error(request, 'Algum erro ocorreu: ' + str(e))

        finally:
            return redirect(reverse(
                'gatheros_subscription:fields-config',
                kwargs={'event_pk': self.kwargs['event_pk']}
            ))

    def can_access(self):
        can_access = super(EventFormFieldReorderView, self).can_access()
        event = self._get_event()
        same_org = event.organization.pk == self.organization.pk
        same_event = self.object.form.event.pk == event.pk
        not_default = self.object.form_default_field is False
        can_change = self.request.user.has_perm(
            'gatheros_subscription.change_field',
            self.object
        ) if not_default else False

        return same_org and can_access and same_event and can_change
