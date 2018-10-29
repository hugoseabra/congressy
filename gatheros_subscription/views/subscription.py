from datetime import datetime

from django.conf import settings
from django.contrib import messages
from django.db.transaction import atomic
from django.forms.models import model_to_dict
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils import six
from django.utils.decorators import classonlymethod
from django.views import generic

from attendance.helpers.attendance import subscription_has_certificate
from core.forms.cleaners import clear_string
from core.views.mixins import TemplateNameableMixin
from gatheros_event.helpers.account import update_account
from gatheros_event.helpers.event_business import is_paid_event
from gatheros_event.models import Event, Person
from gatheros_event.views.mixins import EventDraftStateMixin, \
    AccountMixin, PermissionDenied, EventViewMixin
from gatheros_subscription.directors import SubscriptionSurveyDirector
from gatheros_subscription.forms import (
    SubscriptionPersonForm,
    SubscriptionFilterForm,
    SubscriptionForm,
)
from gatheros_subscription.helpers.export import export_event_data
from gatheros_subscription.helpers.report_payment import \
    PaymentReportCalculator
from gatheros_subscription.helpers.voucher import create_voucher, get_voucher_file_name
from gatheros_subscription.models import (
    FormConfig,
    Lot,
    Subscription,
)
from mailer import exception as mailer_exception, services as mailer
from payment import forms
from payment.helpers import payment_helpers
from payment.models import Transaction
from survey.models import Question, Answer


class SubscriptionViewMixin(TemplateNameableMixin,
                            AccountMixin, EventDraftStateMixin):
    """ Mixin de view para vincular com informações de event. """

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
        return self.get_event().lots.filter(
            internal=False,
        ).order_by('name', 'date_end')

    def get_num_lots(self):
        """ Recupera número de lotes a serem usados nas inscrições. """
        lot_qs = self.get_lots()
        return lot_qs.count() if lot_qs else 0

    def can_access(self):
        if not self.event:
            return False

        return self.event.organization == self.organization


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

        return kwargs

    def get_form(self, form_class=None):
        form = super().get_form(form_class)

        lot_pk = self.request.GET.get('lot', 0)

        if not lot_pk and self.subscription:
            form.check_requirements(lot=self.subscription.lot)

        else:
            try:
                lot = self.event.lots.get(pk=int(lot_pk) if lot_pk else 0)
                form.check_requirements(lot=lot)

            except Lot.DoesNotExist:
                pass

        return form

    def get_subscription_form(self, person, lot_pk):
        data = {
            'person': person.pk,
            'lot': lot_pk,
            'created_by': self.request.user.pk,
        }

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
            if lot.status == lot.LOT_STATUS_RUNNING
               or (self.subscription and self.subscription.lot == lot)
        ]

        context['subscription'] = self.subscription

        lot_pk = self.request.GET.get('lot', 0)
        if not lot_pk and self.subscription:
            context['selected_lot'] = self.subscription.lot.pk

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


class SubscriptionListView(SubscriptionViewMixin, generic.ListView):
    """ Lista de inscrições """

    model = Subscription
    template_name = 'subscription/list.html'
    has_filter = False

    def get_queryset(self):
        query_set = super(SubscriptionListView, self).get_queryset()

        lots = self.request.GET.getlist('lots', [])
        if lots:
            query_set = query_set.filter(lot_id__in=lots)
            self.has_filter = True

        has_profile = self.request.GET.get('has_profile')
        if has_profile:
            query_set = query_set.filter(person__user__isnull=False)
            self.has_filter = True

        event = self.get_event()

        return query_set.filter(event=event, completed=True)

    def get_context_data(self, **kwargs):
        cxt = super().get_context_data(**kwargs)

        cxt.update({
            'can_add_subscription': self.can_add_subscription(),
            'lots': self.get_lots(),
            'has_filter': self.has_filter,
            'event_is_paid': is_paid_event(self.event),
            'has_inside_bar': True,
            'active': 'inscricoes',
        })
        return cxt

    def can_access(self):
        return self.request.user.has_perm(
            'gatheros_event.can_manage_subscriptions',
            self.get_event()
        )

    def can_add_subscription(self):
        event = self.get_event()
        if event.subscription_type == event.SUBSCRIPTION_SIMPLE:
            return True

        num_lots = self.get_num_lots()
        return num_lots > 0


class SubscriptionViewFormView(SubscriptionViewMixin, generic.DetailView):
    template_name = 'subscription/view.html'
    object = None
    queryset = Subscription.objects.get_queryset()
    financial = False
    last_transaction = None

    def get_form(self, **kwargs):
        return forms.ManualTransactionForm(
            subscription=self.get_object(),
            **kwargs
        )

    def get(self, request, *args, **kwargs):

        storage = messages.get_messages(request)

        messenger = []
        for message in list(storage):
            level_tag = message.level_tag
            if level_tag == 'danger':
                level_tag = 'error'

            messenger.append({
                'type': level_tag,
                'message': message.message,
            })

        storage._loaded_messages.clear()

        context = self.get_context_data(messenger=messenger)
        return self.render_to_response(context)

    def dispatch(self, request, *args, **kwargs):
        self.last_transaction = self._get_last_transaction()
        self.object = self.get_object()

        response = super().dispatch(request, *args, **kwargs)

        if self.financial is True:
            has_payable_products = self.object.subscription_products.filter(
                optional_price__gt=0
            ).count() > 0
            has_payable_services = self.object.subscription_services.filter(
                optional_price__gt=0
            ).count() > 0

            if not has_payable_products \
                    and not has_payable_services \
                    and self.object.free:
                messages.warning(
                    request,
                    'Este evento não possui relatório financeiro.'
                )

                return redirect(
                    'subscription:subscription-view',
                    event_pk=self.event.pk,
                    pk=self.object.pk,
                )

        return response

    def _get_last_transaction(self):
        """
        Recupera a transação mais recente.
        Primeiro verificando se há alguma paga. Se não, pega a mais recente.
        """
        queryset = self.get_object().transactions

        paid_transactions = queryset \
            .filter(status=Transaction.PAID) \
            .order_by('-date_created')

        if paid_transactions.count() > 0:
            return paid_transactions.first()

        return queryset.all().order_by('-date_created').first()

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        calculator = PaymentReportCalculator(subscription=self.get_object())

        ctx['object'] = self.object
        ctx['lots'] = calculator.lots
        ctx['transactions'] = calculator.transactions
        ctx['full_prices'] = calculator.full_prices
        ctx['installments'] = calculator.installments
        ctx['has_manual'] = calculator.has_manual
        ctx['survey_answers'] = self.get_survey_answers()
        ctx['total_paid'] = calculator.total_paid
        ctx['dividend_amount'] = calculator.dividend_amount
        ctx['financial'] = self.financial
        ctx['last_transaction'] = self.last_transaction
        ctx['form'] = self.get_checkout_form()
        ctx['encryption_key'] = settings.PAGARME_ENCRYPTION_KEY
        ctx['services'] = self.get_services()
        ctx['products'] = self.get_products()
        ctx['new_boleto_allowed'] = payment_helpers.is_boleto_allowed(
            self.event
        )

        if self.request.GET.get('details'):
            ctx['show_details'] = True

        if 'manual_payment_form' not in ctx:
            ctx['manual_payment_form'] = self.get_form()

        return ctx

    def post(self, request, *args, **kwargs):
        url = reverse('subscription:subscription-payments', kwargs={
            'event_pk': self.event.pk,
            'pk': self.object.pk,
        })

        data = request.POST.copy()

        action = data.get('action')
        next_url = data.get('next_url')
        if action == 'notify_boleto':
            if next_url:
                url = next_url

            last_transaction = self._get_last_transaction()
            if not last_transaction.subscription.person.email:
                messages.error(request, 'Participante não possui e-mail.')
                return redirect(url)

            try:
                mailer.notify_open_boleto(
                    transaction=self._get_last_transaction()
                )
                messages.success(request, 'Boleto enviado com sucesso.')

            except mailer_exception.NotifcationError as e:
                messages.error(request, str(e))

            return redirect(url)

        if not self.event.feature_configuration.feature_manual_payments:
            self.permission_denied_url = reverse(
                'subscription:subscription-list', kwargs={
                    'event_pk': self.event.pk,
                }
            )
            raise PermissionDenied('Você não pode realizar esta ação.')

        data['manual_author'] = '{} ({})'.format(
            request.user.get_full_name(),
            request.user.email,
        )
        data['paid'] = True
        kwargs = {'data': data}

        transaction_id = data.get('transaction_id')

        if transaction_id:
            instance = get_object_or_404(Transaction, pk=transaction_id)
            kwargs.update({'instance': instance})

        form = self.get_form(**kwargs)

        if not form.is_valid():
            return self.render_to_response(self.get_context_data(
                manual_payment_form=form,
                transaction_pk=transaction_id,
                modal='manual-payment',
            ))

        form.save()

        if transaction_id:
            messages.success(request, 'Recebimento editado com sucesso.')
        else:
            messages.success(request, 'Recebimento registrado com sucesso.')

        return redirect(url + '?details=1')

    def get_checkout_form(self):
        return forms.PagarMeCheckoutForm(
            initial={
                'subscription': self.object.pk,
                'next_url': reverse(
                    'subscription:subscription-payments',
                    kwargs={
                        'event_pk': self.event.pk,
                        'pk': self.object.pk,
                    }
                ),
            }
        )

    def get_products(self):
        return self.object.subscription_products.all()

    def get_services(self):
        return self.object.subscription_services.all()

    def get_survey_answers(self):
        survey_answers = list()

        if not self.object.lot.event_survey:
            return survey_answers

        survey = self.object.lot.event_survey.survey

        if self.object.author:
            questions = Question.objects.filter(survey=survey).order_by(
                'order')

            file_types = [
                Question.FIELD_INPUT_FILE_PDF,
                Question.FIELD_INPUT_FILE_IMAGE,
            ]

            for question in questions:

                answer = '-'

                answers = Answer.objects.filter(
                    question=question,
                    author=self.object.author,
                )

                if answers.count() == 1:
                    answer = answers.first()
                elif answers.count() > 1:
                    raise Exception('Temos ambiguidade de respostas')
                elif answers.count() == 0:
                    try:
                        answer = Answer.objects.get(question=question,
                                                    author=self.object.author)
                    except Answer.DoesNotExist:
                        continue

                survey_answers.append({
                    'question': question.label,
                    'human_display': answer.human_display,
                    'value': answer.value,
                    'is_file': question.type in file_types,
                })

        return survey_answers


class SubscriptionAddFormView(SubscriptionFormMixin):
    """ Formulário de inscrição """
    success_message = 'Inscrição criada com sucesso.'

    def get_success_url(self):
        if self.success_message:
            messages.success(self.request, self.success_message)

        if not self.subscription.free:
            return reverse('subscription:subscription-payments', kwargs={
                'event_pk': self.event.pk,
                'pk': self.subscription.pk,
            })

        return reverse('subscription:subscription-view', kwargs={
            'event_pk': self.event.pk,
            'pk': self.subscription.pk,
        })

    def get_error_url(self):
        return reverse('subscription:subscription-add', kwargs={
            'event_pk': self.event.pk
        })

    def get_context_data(self, **kwargs):

        survey_form = kwargs.pop('survey_form', None)

        future_status = Lot.LOT_STATUS_NOT_STARTED
        finished_status = Lot.LOT_STATUS_FINISHED
        running_status = Lot.LOT_STATUS_RUNNING

        context = super().get_context_data(**kwargs)
        context['running_lots'] = \
            self._get_lots_with_status(running_status)
        context['stopped_lots'] = \
            self._get_lots_with_status(finished_status)
        context['future_lots'] = \
            self._get_lots_with_status(future_status)

        if context['selected_lot'] != 0:
            try:

                lot_pk = context['selected_lot']

                lot = Lot.objects.get(pk=lot_pk)
                if lot.event_survey:
                    if survey_form:
                        context['survey_form'] = survey_form
                    else:
                        survey = lot.event_survey.survey
                        context['survey_form'] = self.get_survey_form(survey)
            except Lot.DoesNotExist:
                pass

        return context

    def post(self, request, *args, **kwargs):
        """
            Handles POST requests, instantiating a form instance with the passed
            POST variables and then checked for validity.
        """
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

        form = self.get_form()
        if form.is_valid():

            lot_pk = self.request.POST.get('subscription-lot')
            if not lot_pk:
                lot_pk = self.subscription.lot.pk

            with atomic():
                self.object = form.save()
                subscription_form = self.get_subscription_form(
                    person=self.object,
                    lot_pk=lot_pk,
                )
                if not subscription_form.is_valid():

                    for name, error in subscription_form.errors.items():
                        form.add_error(field='__all__', error=error[0])

                    return self.form_invalid(form)

                self.subscription = subscription_form.save()

                survey_form = None
                if self.subscription.lot.event_survey:

                    survey = self.subscription.lot.event_survey.survey

                    survey_form = self.get_survey_form(
                        survey=survey,
                        data=self.request.POST,
                        files=self.request.FILES,
                        subscription=self.subscription,
                    )

                    if survey_form.is_valid():
                        survey_form.save()
                    else:
                        return self.form_invalid(form, survey_form=survey_form)

                # Criação de Transaction caso seja pago
                trans_type = Transaction.MANUAL_WAITING_PAYMENT
                trans_form = forms.ManualTransactionForm(
                    subscription=self.subscription,
                    data={
                        'manual_author': '{} ({})'.format(
                            request.user.get_full_name(),
                            request.user.email,
                        ),
                        'paid': False,
                        'manual_payment_type': trans_type,
                        'amount': self.subscription.lot.get_calculated_price()
                    }
                )
                if not trans_form.is_valid():
                    return self.form_invalid(form, survey_form=survey_form)

                trans_form.save()
                return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_invalid(self, form, survey_form=None):
        """
        If the form is invalid, re-render the context data with the
        data-filled form and errors.
        """
        return self.render_to_response(
            self.get_context_data(form=form, survey_form=survey_form))

    def get_survey_form(self, survey, subscription=None, data=None,
                        files=None):

        survey_director = SubscriptionSurveyDirector(subscription)

        survey_form = survey_director.get_active_form(
            survey=survey,
            data=data,
            files=files,
            update=self.request.method in ['POST', 'PUT'],
        )

        return survey_form

    def _get_lots_with_status(self, status):
        lot_list = list()

        for lot in self.get_lots().filter():
            if lot.status == status:
                lot_list.append(lot)

        return lot_list


class SubscriptionEditFormView(SubscriptionFormMixin):
    """ Formulário de inscrição """
    success_message = 'Inscrição atualizada com sucesso.'
    allow_edit_lot = False

    def get_success_url(self):
        if self.success_message:
            messages.success(self.request, self.success_message)

        return reverse('subscription:subscription-view', kwargs={
            'event_pk': self.event.pk,
            'pk': self.subscription.pk,
        })

    def get_error_url(self):
        return reverse('subscription:subscription-edit', kwargs={
            'event_pk': self.event.pk,
            'pk': self.subscription.pk,
        })

    def get_context_data(self, **kwargs):

        survey_form = kwargs.pop('survey_form', None)

        context = super().get_context_data(**kwargs)

        if self.subscription.lot.event_survey:
            if survey_form is not None:
                context['survey_form'] = survey_form
            else:
                survey = self.subscription.lot.event_survey.survey

                context['survey_form'] = self.get_survey_form(
                    survey,
                    subscription=self.subscription
                )

        context['stopped_lots'] = [
            lot
            for lot in self.get_lots()
            if lot.status == lot.LOT_STATUS_FINISHED
        ]
        context['running_lots'] = [
            lot
            for lot in self.get_lots()
            if lot.status == lot.LOT_STATUS_RUNNING
        ]
        context['future_lots'] = [
            lot
            for lot in self.get_lots()
            if lot.status == lot.LOT_STATUS_NOT_STARTED
        ]

        if context['selected_lot'] != 0:
            try:

                lot_pk = context['selected_lot']

                lot = Lot.objects.get(pk=lot_pk)
                if lot.event_survey:
                    if survey_form:
                        context['survey_form'] = survey_form
                    else:
                        survey = lot.event_survey.survey
                        context['survey_form'] = self.get_survey_form(survey)
            except Lot.DoesNotExist:
                pass

        return context

    def post(self, request, *args, **kwargs):
        """
            Handles POST requests, instantiating a form instance with the passed
            POST variables and then checked for validity.
        """
        if 'subscription-lot' not in request.POST:
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

        form = self.get_form()
        if form.is_valid():

            lot_pk = self.request.POST.get('subscription-lot')
            if not lot_pk:
                lot_pk = self.subscription.lot.pk

            with atomic():
                self.object = form.save()
                subscription_form = self.get_subscription_form(
                    person=self.object,
                    lot_pk=lot_pk,
                )
                if not subscription_form.is_valid():

                    for name, error in subscription_form.errors.items():
                        form.add_error(field=None, error=error[0])

                    return self.form_invalid(form)

                self.subscription = subscription_form.save()
                if self.subscription.lot.event_survey:

                    survey = self.subscription.lot.event_survey.survey

                    survey_form = self.get_survey_form(
                        survey=survey,
                        data=self.request.POST,
                        files=self.request.FILES,
                        subscription=self.subscription,
                    )

                    if survey_form.is_valid():
                        survey_form.save()
                        return self.form_valid(form)
                    else:
                        return self.form_invalid(form, survey_form=survey_form)

                return self.form_valid(form)

        else:
            return self.form_invalid(form)

    def form_invalid(self, form, survey_form=None):
        """
        If the form is invalid, re-render the context data with the
        data-filled form and errors.
        """
        return self.render_to_response(
            self.get_context_data(form=form, survey_form=survey_form))

    def get_survey_form(self, survey, subscription=None, data=None,
                        files=None):

        survey_director = SubscriptionSurveyDirector(subscription)

        survey_form = survey_director.get_active_form(
            survey=survey,
            data=data,
            files=files,
            update=self.request.method in ['POST', 'PUT'],
        )

        return survey_form


class SubscriptionConfirmationView(SubscriptionViewMixin,
                                   generic.TemplateView):
    """ Inscrição de pessoa que já possui perfil. """
    subscription_user = None
    submitted_data = None
    template_name = 'subscription/subscription_confirmation.html'

    @classonlymethod
    def as_view(cls, user, submitted_data, **initkwargs):

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


class SubscriptionCancelView(EventViewMixin,
                             SubscriptionViewMixin, generic.DetailView):
    template_name = 'subscription/delete.html'
    model = Subscription
    success_message = 'Inscrição cancelada com sucesso.'
    cancel_message = 'Tem certeza que deseja cancelar?'
    model_protected_message = 'A entidade não pode ser cancelada.'
    place_organization = None
    object = None

    def get_object(self, queryset=None):
        """ Resgata objeto principal da view. """
        if not self.object:
            self.object = super(SubscriptionCancelView, self).get_object(
                queryset)

        return self.object

    def pre_dispatch(self, request):
        self.object = self.get_object()
        super(SubscriptionCancelView, self).pre_dispatch(request)

    def get_permission_denied_url(self):
        url = self.get_success_url()
        return url.format(**model_to_dict(self.object)) if self.object else url

    def get_context_data(self, **kwargs):
        context = super(SubscriptionCancelView, self).get_context_data(
            **kwargs)
        context['organization'] = self.organization
        context['go_back_path'] = self.get_success_url()
        context['has_inside_bar'] = True
        context['active'] = 'inscricoes'

        # noinspection PyProtectedMember
        verbose_name = self.object._meta.verbose_name
        context['title'] = 'Cancelar {}'.format(verbose_name)

        data = model_to_dict(self.get_object())
        cancel_message = self.get_cancel_message()
        context['cancel_message'] = cancel_message.format(**data)
        return context

    def get_cancel_message(self):
        """
        Recupera mensagem de remoção a ser perguntada ao usuário antes da
        remoção.
        """
        return self.cancel_message

    def post(self, request, *args, **kwargs):
        try:

            pk = kwargs.get('pk')
            self.object = Subscription.objects.get(pk=pk)
            self.object.status = self.object.CANCELED_STATUS
            self.object.save()

            messages.success(request, self.success_message)

        except Exception as e:
            messages.error(request, str(e))

        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse('subscription:subscription-list', kwargs={
            'event_pk': self.kwargs.get('event_pk')
        })


class MySubscriptionsListView(AccountMixin, generic.ListView):
    """ Lista de inscrições """

    model = Subscription
    template_name = 'subscription/my_subscriptions.html'
    ordering = ('event__name', 'event__date_start', 'event__date_end',)
    has_filter = False
    permission_denied_url = reverse_lazy('front:start')

    def get_queryset(self):
        person = self.request.user.person
        query_set = super(MySubscriptionsListView, self).get_queryset()

        # notcheckedin = self.request.GET.get('notcheckedin')
        # if notcheckedin:
        #     query_set = query_set.filter(attended=False)
        #     self.has_filter = True
        #
        # pastevents = self.request.GET.get('pastevents')
        # now = datetime.now()
        # if pastevents:
        #     query_set = query_set.filter(event__date_end__lt=now)
        #     self.has_filter = True
        #
        # else:
        #     query_set = query_set.filter(event__date_start__gt=now)

        return query_set.filter(
            person=person,
            completed=True, test_subscription=False
            # event__published=True,
        )

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)

        if self.get_paginate_by(self.object_list) is not None and hasattr(
                self.object_list, 'exists'):
            is_empty = not self.object_list.exists()
        else:
            is_empty = len(self.object_list) == 0

        if is_empty:
            return redirect(reverse('event:event-list'))

        return response

    def get_context_data(self, **kwargs):
        cxt = super(MySubscriptionsListView, self).get_context_data(**kwargs)
        cxt['has_filter'] = self.has_filter
        cxt['filter_events'] = self.get_events()
        cxt['status_events'] = self.get_attendance_status_events()
        cxt['needs_boleto_link'] = self.check_if_needs_boleto_link()
        # cxt['filter_categories'] = self.get_categories()
        return cxt

    def get_categories(self):
        """ Resgata categorias das inscrições existentes. """
        queryset = self.get_queryset()
        return queryset.values(
            'event__category__name',
            'event__category__id'
        ).distinct().order_by('event__category__name')

    def get_events(self):
        """ Resgata eventos dos inscrições o usuário possui inscrições. """
        queryset = self.get_queryset()
        return queryset.values(
            'event__name',
            'event__id',
        ).distinct().order_by('event__name')

    def get_attendance_status_events(self):
        status_events = []
        subscription = self.get_queryset()
        for sub in subscription:
            checked = subscription_has_certificate(sub.pk)
            status_events.append({
                'event_pk': sub.event.id,
                'checked': checked
            })

        return status_events

    def can_access(self):
        try:
            self.request.user.person
        except Person.DoesNotExist:
            return False
        else:
            return True

    def check_if_needs_boleto_link(self):
        for subscription in self.object_list:

            if subscription.status == subscription.AWAITING_STATUS:

                for transaction in subscription.transactions.all():
                    if transaction.status == transaction.WAITING_PAYMENT and \
                            transaction.type == 'boleto':
                        return True

        return False


class SubscriptionExportView(SubscriptionViewMixin, generic.View):
    http_method_names = ['post']
    template_name = 'subscription/export.html'
    form_class = SubscriptionFilterForm
    model = Subscription
    paginate_by = 5
    allow_empty = True
    event = None

    def get_event(self):
        if self.event:
            return self.event

        self.event = get_object_or_404(Event, pk=self.kwargs.get('event_pk'))
        return self.event

    def post(self, request, *args, **kwargs):
        # Chamando exportação
        output = export_event_data(self.get_event())

        # Criando resposta http com arquivo de download
        response = HttpResponse(
            output,
            content_type="application/vnd.ms-excel"
        )

        # Definindo nome do arquivo
        event = self.get_event()
        name = "%s_%s.xlsx" % (
            event.slug,
            datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        )
        response['Content-Disposition'] = 'attachment; filename=%s' % name

        return response

    def can_access(self):
        return self.request.user.has_perm(
            'gatheros_event.can_manage_subscriptions',
            Event.objects.get(pk=self.kwargs.get('event_pk'))
        )


class VoucherSubscriptionPDFView(AccountMixin):

    def pre_dispatch(self, request):
        uuid = self.kwargs.get('pk')
        self.subscription = get_object_or_404(Subscription,
                                              uuid=uuid)

        return super().pre_dispatch(request)

    def get(self, request, *args, **kwargs):
        pdf = create_voucher(subscription=self.subscription)
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'inline; filename="{}"'.format(
            get_voucher_file_name(subscription=self.subscription)
        )

        return response


class SwitchSubscriptionTestView(SubscriptionViewMixin, generic.View):
    """
    Gerenciamento de inscrições que podem ou não serem setados como Teste.
    """
    success_message = ""

    def get_object(self):
        return get_object_or_404(Subscription, pk=self.kwargs.get('pk'))

    def post(self, request, *args, **kwargs):
        state = request.POST.get('state')

        subscription = self.get_object()
        subscription.test_subscription = state == "True"
        subscription.save()
        return HttpResponse(status=200)
