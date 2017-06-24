from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views import generic

from gatheros_event.models import Event
from gatheros_event.views.mixins import AccountMixin
from gatheros_subscription.forms import SubscriptionForm
from gatheros_subscription.models import Subscription


class SubscriptionListView(AccountMixin, generic.ListView):
    """ Lista de inscrições """

    model = Subscription
    template_name = 'gatheros_subscription/subscription/list.html'
    event = None

    def get_permission_denied_url(self):
        return reverse('gatheros_event:event-panel', kwargs={
            'pk': self.kwargs.get('event_pk')
        })

    def get_context_data(self, **kwargs):
        context = super(SubscriptionListView, self).get_context_data(**kwargs)
        context['event'] = self.get_event()

        return context

    def get_queryset(self):
        query_set = super(SubscriptionListView, self).get_queryset()
        event = self.get_event()

        return query_set.filter(event=event)

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
        return self.request.user.has_perm(
            'gatheros_event.can_manage_subscriptions',
            self.get_event()
        )


class SubscriptionAddFormView(AccountMixin, generic.FormView):
    """ Formulário de inscrição """

    form_class = SubscriptionForm
    template_name = 'gatheros_subscription/subscription/form.html'
    event = None

    def get_permission_denied_url(self):
        return reverse('gatheros_subscription:subscription-list', kwargs={
            'event_pk': self.kwargs.get('event_pk')
        })

    def get_context_data(self, **kwargs):
        cxt = super(SubscriptionAddFormView, self).get_context_data(**kwargs)
        cxt.update({
            'event': self._get_event(),
            'form_title': 'Pré-inscrição'
        })

        internal_form_fields = []
        hidden_fields = []
        default_fields = []
        additional_fields = []

        form = cxt['form']
        for form_field in form:
            field = form.get_gatheros_field_by_name(form_field.name)
            if not field:
                if form_field.is_hidden:
                    hidden_fields.append(form_field)
                else:
                    internal_form_fields.append(form_field)

                continue

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
            'internal_form_fields': internal_form_fields,
            'hidden_fields': hidden_fields,
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
            hide_lot=False,
            **self.get_form_kwargs()
        )

    def can_access(self):
        event = self._get_event()
        enabled = event.subscription_type != event.SUBSCRIPTION_DISABLED
        can_view = self.request.user.has_perm(
            'gatheros_subscription.change_form',
            event.form
        ) if enabled else False

        return enabled and can_view

    def _get_event(self):
        """ Resgata evento do contexto """
        if not self.event:
            pk = self.kwargs.get('event_pk')
            self.event = get_object_or_404(Event, pk=pk)

        return self.event


class SubscriptionEditFormView(SubscriptionAddFormView):
    object = None

    def get_form_kwargs(self):
        kwargs = super(SubscriptionEditFormView, self).get_form_kwargs()
        kwargs.update({'instance': self.object})

        return kwargs

    def dispatch(self, request, *args, **kwargs):
        self.object = get_object_or_404(Subscription, pk=self.kwargs.get('pk'))

        return super(SubscriptionEditFormView, self).dispatch(
            request,
            *args,
            **kwargs
        )

    def get_context_data(self, **kwargs):
        cxt = super(SubscriptionEditFormView, self).get_context_data(**kwargs)
        cxt.update({
            'object': self.object
        })

        return cxt
