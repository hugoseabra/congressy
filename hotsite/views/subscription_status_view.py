"""
    View usada para verificar o status da sua inscrição
"""

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import User
from django.shortcuts import redirect
from django.views import generic

from gatheros_event.helpers.event_business import is_paid_event
from hotsite.views import SubscriptionFormMixin
from payment.models import Transaction


class SubscriptionStatusView(SubscriptionFormMixin, generic.TemplateView):
    template_name = 'hotsite/subscription_status.html'

    def __init__(self, **initkwargs):
        self.event = None
        self.person = None
        self.subscription = None
        self.transactions = None
        self.restart_private_event = False
        super().__init__(**initkwargs)

    def pre_dispatch(self):
        super().pre_dispatch()

        self.event = self.current_event.event
        self.person = self.current_subscription.person
        self.subscription = self.current_subscription.subscription

    def dispatch(self, request, *args, **kwargs):

        slug = self.kwargs.get('slug')

        if not slug:
            return redirect('https://congressy.com')

        if not request.user.is_authenticated:
            return redirect('public:hotsite', slug=slug)

        self.pre_dispatch()

        # Se  não há lotes pagos, não há o que fazer aqui.
        if not is_paid_event(self.event):
            return redirect('public:hotsite', slug=self.event.slug)

        if self.subscription.completed is False:
            messages.error(
                message='Você não possui inscrição neste evento.',
                request=request
            )
            return redirect('public:hotsite', slug=slug)

        if not self.current_subscription.transactions:
            if self.current_event.is_private_event():
                self.request.session['has_private_subscription'] = \
                    str(self.subscription.pk)
            else:
                messages.warning(
                    message='Por favor, informe um lote para realizar o'
                            ' pagamento ao final do processo de inscrição.',
                    request=request
                )

            return redirect('public:hotsite-subscription', slug=slug)

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        has_paid_transaction = False

        is_new = self.current_subscription.subscription.is_new
        context['is_subscribed'] = is_new is False

        context['person'] = self.subscription.person
        context['allow_transaction'] = self.get_allowed_transaction()
        context['transactions'] = self.current_subscription.transactions

        can_reprocess_payment = True

        for trans in self.current_subscription.payments:
            is_cc = trans.type == Transaction.CREDIT_CARD
            is_boleto = trans.type == Transaction.BOLETO
            if trans.status == Transaction.PAID:
                has_paid_transaction = True

            if is_boleto and trans.status == Transaction.PROCESSING:
                can_reprocess_payment = False

            if is_cc and trans.status in \
                    [Transaction.WAITING_PAYMENT, Transaction.PROCESSING]:
                can_reprocess_payment = False

        context['can_reprocess_payment'] = can_reprocess_payment
        context['has_paid_transaction'] = has_paid_transaction

        context['pagarme_key'] = settings.PAGARME_ENCRYPTION_KEY
        context['remove_preloader'] = True
        context['subscription'] = self.subscription
        context['is_private_event'] = self.current_event.is_private_event()
        context['lot_is_still_valid'] = False

        sub_lot = self.subscription.lot
        lot_running = self.current_event.is_lot_running(sub_lot)

        if sub_lot.private is True and lot_running:
            context['lot_is_still_valid'] = True
            self.request.session['exhibition_code'] = sub_lot.exhibition_code

        return context

    def post(self, request, *args, **kwargs):
        action = request.POST.get('action')

        if action == 'force-coupon':
            lot = self.subscription.lot

            if lot.private is True:
                self.request.session['has_private_subscription'] = \
                    str(self.subscription.pk)

            return redirect('public:hotsite', slug=self.current_event.slug)

        return redirect('public:hotsite-status', slug=self.current_event.slug)

    def subscriber_has_account(self, email):
        if self.request.user.is_authenticated:
            return True

        try:
            User.objects.get(email=email)
            return True

        except User.DoesNotExist:
            pass

        return False

    def get_allowed_transaction(self):

        found_boleto = False
        found_credit_card = False

        try:
            transactions = Transaction.objects.filter(
                subscription=self.subscription)

            for transaction in transactions:
                if transaction.data['payment_method'] == 'boleto':
                    found_boleto = True
                elif transaction.data['payment_method'] == 'credit_card':
                    found_credit_card = True
                if found_boleto and found_credit_card:
                    return False
        except Transaction.DoesNotExist:
            return False

        if found_credit_card:
            return 'boleto'

        if found_boleto:
            return 'credit_card'

        return True
