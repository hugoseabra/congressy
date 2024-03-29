from datetime import timedelta

from django.conf import settings
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views import generic

from gatheros_event.views.mixins import PermissionDenied
from gatheros_subscription.helpers.report_payment import \
    PaymentReportCalculator
from gatheros_subscription.models import (
    Subscription,
)
from gatheros_subscription.views import SubscriptionViewMixin
from mailer import exception as mailer_exception, services as mailer
from payment import forms
from payment.helpers import payment_helpers
from payment.models import Transaction
from survey.models import Question, Answer


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

        if self.object.event_id != self.event.pk:
            messages.warning(
                request,
                'Inscrição inválida para este evento..'
            )

            return redirect(
                'subscription:subscription-list',
                event_pk=self.event.pk,
            )

        if self.financial is True:
            has_payable_products = self.object.subscription_products.filter(
                optional__liquid_price__gt=0
            ).count() > 0
            has_payable_services = self.object.subscription_services.filter(
                optional__liquid_price__gt=0
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
        ctx['manual_form'] = forms.PartManualTransactionForm(self.object)
        ctx['encryption_key'] = settings.PAGARME_ENCRYPTION_KEY
        ctx['services'] = self.get_services()
        ctx['products'] = self.get_products()
        ctx['has_open_installment_contract'] = \
            self.has_open_installment_contract()
        ctx['base_expiration_day'] = self.get_base_expiration_day()
        ctx['installment_limit_date'] = self.get_installment_limit_date()
        ctx['minimum_amount'] = self.get_minimum_amount()

        ctx['new_boleto_allowed'] = payment_helpers.is_boleto_allowed(
            self.event
        )

        if self.request.GET.get('details'):
            ctx['show_details'] = True

        if 'manual_payment_form' not in ctx:
            ctx['manual_payment_form'] = self.get_form()

        if self.event.feature_configuration.feature_checkin:
            ctx['services_attended'] = self.get_services_attended()

            services = self.get_available_attendances()

            ctx['all_services'] = self.event.attendance_services.all()
            ctx['services'] = services
            ctx['has_webhook'] = \
                len([a for a in services if a.printing_queue_webhook]) > 0

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

        elif action == 'notify_voucher':
            if next_url:
                url = next_url

            try:
                mailer.notify_voucher(subscription=self.object)
                messages.success(request, 'Voucher enviado com sucesso.')

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

        manual_type = data.get('manual_payment_type')

        data['paid'] = manual_type != Transaction.MANUAL_WAITING_PAYMENT
        kwargs = {'data': data}

        transaction_id = data.get('transaction_id')

        if transaction_id:
            instance = get_object_or_404(Transaction, pk=transaction_id)
            kwargs.update({'instance': instance})

        if action == 'manual-part':
            if not self.event.feature_configuration.feature_manual_payments:
                self.permission_denied_url = reverse(
                    'subscription:subscription-list', kwargs={
                        'event_pk': self.event.pk,
                    }
                )
                raise PermissionDenied('Você não pode realizar esta ação.')

            form = forms.PartManualTransactionForm(self.object, data=data)

            if form.is_valid():
                form.save()
                messages.success(request, 'Recebimento criado com sucesso.')
                return redirect(url + '?details=1')
            else:
                return self.render_to_response(self.get_context_data())

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

        if not self.object.lot.event_survey_id:
            return survey_answers

        survey = self.object.lot.event_survey.survey

        author = None
        if self.object.person.user_id:
            authors = self.object.person.user.authors.filter(
                survey_id=survey.pk,
            )
            if authors.count():
                author = authors.last()

        elif not author and self.object.author_id:
            author = self.object.author

        if author:
            questions = \
                Question.objects.filter(survey_id=survey.pk).order_by('order')

            file_types = [
                Question.FIELD_INPUT_FILE_PDF,
                Question.FIELD_INPUT_FILE_IMAGE,
            ]

            for question in questions:

                answer = '-'

                answers = Answer.objects.filter(
                    question_id=question.pk,
                    author_id=author.pk,
                )

                if answers.count() == 1:
                    answer = answers.first()
                elif answers.count() > 1:
                    raise Exception('Temos ambiguidade de respostas')
                elif answers.count() == 0:
                    try:
                        answer = Answer.objects.get(question_id=question.pk,
                                                    author_id=author.pk)
                    except Answer.DoesNotExist:
                        continue

                survey_answers.append({
                    'question': question.label,
                    'human_display': answer.human_display,
                    'value': answer.value,
                    'is_file': question.type in file_types,
                })

        return survey_answers

    def has_open_installment_contract(self):
        return self.object.installment_contracts.filter(
            status='open').count() > 0

    def get_installment_limit_date(self):
        date = self.event.date_start - timedelta(days=2)
        return date.strftime('%Y-%m-%d')

    def get_base_expiration_day(self):
        date = self.event.date_start - timedelta(days=2)
        return date.strftime('%d')

    def get_minimum_amount(self):
        return settings.CONGRESSY_MINIMUM_AMOUNT_FOR_INSTALLMENTS

    def get_available_attendances(self):
        checkins = self.get_services_attended()
        pks = [c.attendance_service_id for c in checkins]

        return self.event.attendance_services.all().exclude(
            id__in=pks
        )

    def get_services_attended(self):
        return self.object.checkins.filter(
            checkout__isnull=True,
        )
