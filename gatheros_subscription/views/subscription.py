from datetime import datetime

from django.contrib import messages
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils import six
from django.utils.decorators import classonlymethod
from django.views import generic

from gatheros_event.models import Event
from gatheros_event.views.mixins import AccountMixin, DeleteViewMixin
from gatheros_subscription.forms import SubscriptionForm
from gatheros_subscription.models import Subscription


class EventViewMixin(AccountMixin, generic.View):
    """ Mixin de view para vincular com informações de event. """
    event = None

    def dispatch(self, request, *args, **kwargs):
        self.permission_denied_url = reverse(
            'gatheros_event:event-panel',
            kwargs={'pk': self.kwargs.get('event_pk')}
        )
        return super(EventViewMixin, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        # noinspection PyUnresolvedReferences
        context = super(EventViewMixin, self).get_context_data(**kwargs)
        context['event'] = self.get_event()

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

    def get_lots(self):
        event = self.get_event()
        if event.subscription_type == Event.SUBSCRIPTION_DISABLED:
            return None

        return event.lots.filter(
            date_start__lte=datetime.now(),
            date_end__gt=datetime.now()
        )

    def get_num_lots(self):
        """ Recupera número de lotes a serem usados nas inscrições. """
        lot_qs = self.get_lots()
        return lot_qs.count() if lot_qs else 0


class SubscriptionFormMixin(EventViewMixin, generic.FormView):
    success_message = None
    template_name = 'gatheros_subscription/subscription/form.html'
    object = None

    def get_form_kwargs(self):
        event = self.get_event()

        kwargs = super(SubscriptionFormMixin, self).get_form_kwargs()
        kwargs.update({
            'form': event.form,
            'hide_lot': False,
        })

        return kwargs

    def get_success_url(self):
        return reverse('gatheros_subscription:subscription-list', kwargs={
            'event_pk': self.kwargs.get('event_pk')
        })

    def form_invalid(self, form):
        messages.error(self.request, form.errors)
        return super(SubscriptionFormMixin, self).form_invalid(form)

    def form_valid(self, form):
        try:
            self.object = form.save()

        except Exception as e:
            messages.error(self.request, str(e))
            return self.form_invalid(form)

        else:
            if self.success_message:
                messages.success(self.request, self.success_message)

            return super(SubscriptionFormMixin, self).form_valid(form)


class SubscriptionListView(EventViewMixin, generic.ListView):
    """ Lista de inscrições """

    model = Subscription
    template_name = 'gatheros_subscription/subscription/list.html'

    def get_queryset(self):
        query_set = super(SubscriptionListView, self).get_queryset()
        event = self.get_event()

        return query_set.filter(event=event)

    def get_context_data(self, **kwargs):
        cxt = super(SubscriptionListView, self).get_context_data(**kwargs)
        cxt.update({
            'can_add_subscription': self.can_add_subscription(),
            'lots': self.get_lots()
        })
        return cxt

    def can_access(self):
        return self.request.user.has_perm(
            'gatheros_event.can_manage_subscriptions',
            self.get_event()
        )

    def can_add_subscription(self):
        num_lots = self.get_num_lots()
        return num_lots > 0


class SubscriptionAddFormView(SubscriptionFormMixin):
    """ Formulário de inscrição """

    form_class = SubscriptionForm
    template_name = 'gatheros_subscription/subscription/form.html'
    success_message = 'Pré-inscrição criada com sucesso.'

    def get_context_data(self, **kwargs):
        cxt = super(SubscriptionAddFormView, self).get_context_data(**kwargs)
        cxt.update({
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

    def post(self, request, *args, **kwargs):

        request.POST = request.POST.copy()

        confirmation_reply = request.POST.get('subscription_user_reply')
        confirmation_yes = request.POST.get('confirmation_yes')

        email = request.POST.get('email')

        if email:
            try:
                # Se há usuário e a mesma possui relacionamento com Person
                user = User.objects.get(email=email, person__isnull=False)

                if not confirmation_reply:
                    view = SubscriptionConfirmationView.as_view(
                        user=user,
                        submitted_data=request.POST,
                    )

                    return view(request, *args, **kwargs)
                elif confirmation_yes:
                    request.POST.update({'user': user.pk})

            except User.DoesNotExist:
                pass

        return super(SubscriptionAddFormView, self).post(
            request,
            *args,
            **kwargs
        )

    def can_access(self):
        event = self.get_event()
        num_lots = self.get_num_lots()

        if num_lots == 0:
            self.permission_denied_message = \
                'Lotes não disponíveis.'

            self.permission_denied_url = reverse(
                'gatheros_subscription:subscription-list',
                kwargs={'event_pk': event.pk}
            )

        enabled = event.subscription_type != event.SUBSCRIPTION_DISABLED
        can_manage = self.request.user.has_perm(
            'gatheros_event.can_manage_subscriptions',
            event
        ) if enabled else False

        return can_manage and num_lots > 0


class SubscriptionConfirmationView(EventViewMixin, generic.TemplateView):
    subscription_user = None
    submitted_data = None
    template_name = \
        'gatheros_subscription/subscription/subscription_confirmation.html'

    @classonlymethod
    def as_view(cls, user, submitted_data, **initkwargs):

        del submitted_data['user']

        csrf = submitted_data.get('csrfmiddlewaretoken')
        if csrf:
            del submitted_data['csrfmiddlewaretoken']

        cleaned_submitted_data = {}
        for field_name, value in six.iteritems(dict(submitted_data)):
            if len(value) <= 1:
                cleaned_submitted_data[field_name] = value[0]
            else:
                cleaned_submitted_data[field_name] = value

        cls.subscription_user = user
        cls.submitted_data = cleaned_submitted_data

        return super(SubscriptionConfirmationView, cls).as_view(
            **initkwargs
        )

    def get_context_data(self, **kwargs):
        cxt = super(SubscriptionConfirmationView, self).get_context_data(
            **kwargs
        )
        cxt.update({
            'subscription_user': self.subscription_user,
            'submitted_data': self.submitted_data,
        })

        return cxt

    def post(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)


class SubscriptionEditFormView(SubscriptionAddFormView):
    object = None
    success_message = 'Pré-inscrição alterada com sucesso.'

    def dispatch(self, request, *args, **kwargs):
        self.object = get_object_or_404(Subscription, pk=self.kwargs.get('pk'))

        return super(SubscriptionEditFormView, self).dispatch(
            request,
            *args,
            **kwargs
        )

    def post(self, request, *args, **kwargs):
        # Pula confirmação
        return super(SubscriptionAddFormView, self).post(
            request,
            *args,
            **kwargs
        )

    def get_form_kwargs(self):
        kwargs = super(SubscriptionEditFormView, self).get_form_kwargs()
        kwargs.update({'instance': self.object})

        return kwargs

    def get_context_data(self, **kwargs):
        cxt = super(SubscriptionEditFormView, self).get_context_data(**kwargs)
        cxt.update({
            'object': self.object
        })

        return cxt

    def can_access(self):
        event = self.get_event()
        enabled = event.subscription_type != event.SUBSCRIPTION_DISABLED
        return self.request.user.has_perm(
            'gatheros_event.can_manage_subscriptions',
            event
        ) if enabled else False


class SubscriptionDeleteView(EventViewMixin, DeleteViewMixin):
    model = Subscription
    success_message = 'Pré-inscrição excluída com sucesso.'
    place_organization = None

    def get_permission_denied_url(self):
        return reverse('gatheros_subscription:subscription-list', kwargs={
            'event_pk': self.kwargs.get('event_pk')
        })

    def get_success_url(self):
        return reverse('gatheros_subscription:subscription-list', kwargs={
            'event_pk': self.kwargs.get('event_pk')
        })

    def can_delete(self):
        return self.request.user.has_perm(
            'gatheros_event.can_manage_subscriptions',
            self.get_event()
        )
