from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views import generic

from gatheros_event.models import Event
from gatheros_event.views.mixins import AccountMixin, DeleteViewMixin
from gatheros_subscription.forms import EventConfigForm, EventFormFieldForm
from gatheros_subscription.models import Field


class BaseEventForm(AccountMixin, generic.TemplateView):
    form_title = 'Formulário'
    event = None

    def get_permission_denied_url(self):
        return reverse('gatheros_event:event-panel', kwargs={
            'pk': self.kwargs.get('event_pk')
        })

    def get_context_data(self, **kwargs):
        context = super(BaseEventForm, self).get_context_data(**kwargs)
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
        enabled = event.subscription_type != event.SUBSCRIPTION_DISABLED
        can_view = self.request.user.has_perm(
            'gatheros_subscription.change_form',
            event.form
        ) if enabled else False

        return enabled and can_view


class BaseEventFormFieldForm(BaseEventForm):
    form_class = EventFormFieldForm
    model = EventFormFieldForm.Meta.model
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


class EventConfigFormView(BaseEventForm, generic.FormView):
    form_class = EventConfigForm
    template_name = 'gatheros_subscription/event_form/config.html'
    form_title = 'Configuração de Formulário'

    def get_form(self, form_class=None):
        if not form_class:
            form_class = self.form_class

        event = self._get_event()
        return form_class(form=event.form, **self.get_form_kwargs())


class EventFormFieldAddView(BaseEventFormFieldForm, generic.CreateView):
    form_title = 'Adicionar Campo de Formulário'
    success_message = 'Campo criado com sucesso.'

    def get_success_url(self):
        return reverse(
            'gatheros_subscription:fields-config',
            kwargs={'event_pk': self.kwargs['event_pk']}
        )

    def can_access(self):
        event = self._get_event()
        can_access = super(EventFormFieldAddView, self).can_access()
        can_change = self.request.user.has_perm(
            'gatheros_subscription.can_add_field',
            event.form
        ) if can_access else False

        return can_access and can_change


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
        can_access = super(BaseEventFormFieldForm, self).can_access()
        event_pk = int(self.kwargs.get('event_pk'))
        same_event = self.object.form.event.pk == event_pk
        not_default = self.object.form_default_field is False
        can_change = self.request.user.has_perm(
            'gatheros_subscription.change_field',
            self.object
        )

        return can_access and same_event and not_default and can_change


class EventFormDeleteView(DeleteViewMixin, BaseEventFormFieldForm):
    model = Field
    delete_message = "Tem certeza que deseja excluir o campo \"{name}\"?"
    success_message = "Campo excluído com sucesso!"

    def can_delete(self):
        can_access = self.can_access()
        event_pk = int(self.kwargs.get('event_pk'))
        same_event = self.object.form.event.pk == event_pk
        not_default = self.object.form_default_field is False
        can_change = self.request.user.has_perm(
            'gatheros_subscription.delete_field',
            self.object
        )

        return can_access and same_event and not_default and can_change
