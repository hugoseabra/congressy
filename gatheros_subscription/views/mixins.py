from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views import generic

from core.forms.cleaners import clear_string
from core.views.mixins import TemplateNameableMixin
from gatheros_event.helpers.account import update_account
from gatheros_event.helpers.event_business import is_paid_event
from gatheros_event.models import Event
from gatheros_event.views.mixins import EventDraftStateMixin, \
    AccountMixin, PermissionDenied
from gatheros_subscription.forms import (
    SubscriptionPersonForm,
    SubscriptionForm,
)
from gatheros_subscription.models import FormConfig, Subscription
from ticket.models import Lot


class FeatureFlagMixinBaseMixin(AccountMixin, generic.View,
                                EventDraftStateMixin):
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

        return super().pre_dispatch(request)

    def get_context_data(self, **kwargs):
        # noinspection PyUnresolvedReferences
        context = super().get_context_data(**kwargs)

        context['event'] = self.event
        context['is_paid_event'] = is_paid_event(self.event)

        context.update(self.get_event_state_context_data(self.event))

        return context


class SurveyFeatureFlagMixin(FeatureFlagMixinBaseMixin):
    def pre_dispatch(self, request):
        response = super().pre_dispatch(request)
        features = self.event.feature_configuration

        if features.feature_survey is False:
            if self.request.is_ajax():
                return HttpResponse(status=403)
            raise PermissionDenied(self.get_permission_denied_message())
        return response


class SubscriptionViewMixin(TemplateNameableMixin,
                            AccountMixin, EventDraftStateMixin):
    """ Mixin de view para vincular com informações de event.
        @TODO add ContextMixin
    """

    def __init__(self, **initargs):
        super().__init__(**initargs)
        self.event = None

    def dispatch(self, request, *args, **kwargs):
        self.event = self.get_event()

        update_account(
            request=self.request,
            organization=self.event.organization,
            force=True
        )

        self.permission_denied_url = reverse('event:event-list')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        # noinspection PyUnresolvedReferences
        event = self.get_event()

        context = super().get_context_data(**kwargs)

        context['event'] = event
        context['is_paid_event'] = is_paid_event(event)

        context.update(self.get_event_state_context_data(event))

        try:
            config = FormConfig.objects.get(event=event)
        except FormConfig.DoesNotExist:
            config = FormConfig()
            config.event = event

        if is_paid_event(event):
            config.email = True
            config.phone = True
            config.city = True

            config.cpf = config.CPF_REQUIRED
            config.birth_date = config.BIRTH_DATE_REQUIRED
            config.address = config.ADDRESS_SHOW

        context['config'] = config

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

    def is_by_lots(self):
        return self.event.subscription_type == Event.SUBSCRIPTION_BY_LOTS

    def get_lots(self):
        return Lot.objects.filter(
            ticket__event_id=self.get_event().pk,
        ).order_by('date_start', 'date_end', 'ticket__name')

    def get_num_lots(self):
        """ Recupera número de lotes a serem usados nas inscrições. """
        lot_qs = self.get_lots()
        return lot_qs.count() if lot_qs else 0

    def can_access(self):
        if not self.event:
            return False

        return self.event.organization_id == self.organization.pk


class SubscriptionFormMixin(SubscriptionViewMixin, generic.FormView):
    template_name = 'subscription/form.html'
    form_class = SubscriptionPersonForm
    success_message = None
    subscription = None
    object = None
    allow_edit_lot = True
    error_url = None

    def get_error_url(self):
        return self.error_url

    def pre_dispatch(self, request):
        self.event = self.get_event()

        if self.event.allow_internal_subscription is False:
            self.permission_denied_url = reverse(
                'subscription:subscription-list', kwargs={
                    'event_pk': self.event.pk,
                }
            )
            raise PermissionDenied('Você não pode realizar esta ação.')

    def dispatch(self, request, *args, **kwargs):
        if self.kwargs.get('pk'):
            self.subscription = get_object_or_404(
                Subscription,
                pk=self.kwargs.get('pk')
            )
            self.object = self.subscription.person

            origin = self.subscription.origin
            self.allow_edit_lot = \
                origin == self.subscription.DEVICE_ORIGIN_MANAGE

        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['prefix'] = 'person'

        if self.object:
            kwargs['instance'] = self.object

        if self.subscription:
            initial = kwargs.get('initial', dict()) or dict()

            if self.subscription.tag_info:
                initial['tag_info'] = self.subscription.tag_info

            if self.subscription.tag_group:
                initial['tag_group'] = self.subscription.tag_group

            if self.subscription.obs:
                initial['obs'] = self.subscription.obs

            kwargs.update({'initial': initial})

        return kwargs

    def get_form(self, form_class=None):
        form = super().get_form(form_class)

        lot_pk = self.request.GET.get('lot', 0)

        if not lot_pk and self.subscription:
            form.check_requirements(lot=self.subscription.ticket_lot)

        else:
            try:
                lot = Lot.objects.get(
                    ticket__event_id=self.event.pk,
                    pk=int(lot_pk) if lot_pk else 0
                )
                form.check_requirements(lot=lot)

            except Lot.DoesNotExist:
                pass

        return form

    def get_subscription_form(self, person, lot_pk):
        data = {
            'person': person.pk,
            'ticket_lot': lot_pk,
            'created_by': self.request.user.pk,
        }

        tag_info = self.request.POST.get('person-tag_info')
        if tag_info:
            data.update({'tag_info': tag_info})

        obs = self.request.POST.get('person-obs')
        if obs:
            data.update({'obs': obs})

        tag_group = self.request.POST.get('person-tag_group')
        if tag_group:
            data.update({'tag_group': tag_group})

        kwargs = {}

        if self.subscription:
            kwargs['instance'] = self.subscription

            if self.subscription.origin:
                data['origin'] = self.subscription.origin
            else:
                data['origin'] = Subscription.DEVICE_ORIGIN_MANAGE
        else:
            data['origin'] = Subscription.DEVICE_ORIGIN_MANAGE

        kwargs.update({'data': data})

        return SubscriptionForm(self.event, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['has_inside_bar'] = True
        context['active'] = 'inscricoes'

        context['object'] = self.object
        context['allow_edit_lot'] = self.allow_edit_lot

        context['lots'] = [
            lot
            for lot in self.get_lots()
            if lot.running or (
                        self.subscription and self.subscription.ticket_lot_id == lot.pk)
        ]

        context['subscription'] = self.subscription
        context['selected_ticket_name'] = None

        lot_pk = self.request.GET.get('lot', 0)
        if not lot_pk and self.subscription:
            context['selected_lot'] = self.subscription.ticket_lot_id
        else:
            context['selected_lot'] = int(lot_pk) if lot_pk else 0

        return context

    def post(self, request, *args, **kwargs):
        if self.allow_edit_lot and 'subscription-lot' not in request.POST:
            messages.warning(request, 'Você deve informar um lote.')
            return redirect(self.get_error_url())

        request.POST = request.POST.copy()

        to_be_pre_cleaned = [
            'person-cpf',
            'person-phone',
            'person-zip_code',
            'person-institution_cnpj'
        ]

        for field in to_be_pre_cleaned:
            if field in request.POST:
                request.POST[field] = clear_string(request.POST[field])

        return super().post(request, *args, **kwargs)

    def form_valid(self, form):

        return super().form_valid(form)
