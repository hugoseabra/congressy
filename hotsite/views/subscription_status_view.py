"""
    View usada para verificar o status da sua inscrição
"""
from datetime import datetime

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404, redirect
from django.views import generic

from gatheros_event.models import Event
from gatheros_subscription.models import Subscription
from hotsite.views import EventMixin
from payment.models import Transaction


class SubscriptionStatusView(EventMixin, generic.TemplateView):
    template_name = 'hotsite/subscription_status.html'
    person = None
    subscription = None
    event = None
    transactions = None
    restart_private_event = False

    def dispatch(self, request, *args, **kwargs):

        slug = self.kwargs.get('slug')

        if not slug:
            return redirect('https://congressy.com')
        self.event = get_object_or_404(Event, slug=slug)

        if not request.user.is_authenticated:
            return redirect('public:hotsite', slug=self.event.slug)

        self.person = self.get_person()

        # Se  não há lotes pagos, não há o que fazer aqui.
        if not self.has_paid_lots() and not self.has_paid_optionals():
            return redirect('public:hotsite', slug=self.event.slug)

        try:
            self.subscription = Subscription.objects.get(
                event=self.event,
                person=self.person,
                completed=True, test_subscription=False
            )

            if not self.get_transactions():
                if self.is_private_event():
                    self.request.session['has_private_subscription'] = \
                        str(self.subscription.pk)
                else:
                    messages.warning(
                        message='Por favor, informe um lote para realizar o'
                                ' pagamento ao final do processo de inscrição.',
                        request=request
                    )

                return redirect(
                    'public:hotsite-subscription',
                    slug=self.event.slug
                )

        except Subscription.DoesNotExist:
            messages.error(
                message='Você não possui inscrição neste evento.',
                request=request
            )
            return redirect('public:hotsite', slug=self.event.slug)

        return super().dispatch(request, *args, **kwargs)

    def has_paid_optionals(self):
        """ Retorna se evento possui algum lote pago. """

        try:
            sub = Subscription.objects.get(
                person=self.person,
                event=self.event,
                completed=True, test_subscription=False
            )

            has_products = sub.subscription_products.filter(
                optional_price__gt=0
            ).count() > 0

            has_services = sub.subscription_services.filter(
                optional_price__gt=0
            ).count() > 0

            return has_products is True or has_services is True

        except Subscription.DoesNotExist:
            return False

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        has_paid_transaction = False

        context['person'] = self.get_person()
        context['is_subscribed'] = self.is_subscribed()
        context['allow_transaction'] = self.get_allowed_transaction()
        all_transactions = self.get_transactions()
        context['transactions'] = all_transactions

        can_reprocess_payment = True

        for trans in all_transactions:
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
        context['is_private_event'] = self.is_private_event()
        context['lot_is_still_valid'] = False

        lot = self.subscription.lot

        if lot.private is True and lot.status == lot.LOT_STATUS_RUNNING:
            context['lot_is_still_valid'] = True
            self.request.session['exhibition_code'] = lot.exhibition_code

        return context

    def post(self, request, *args, **kwargs):
        action = request.POST.get('action')

        if action == 'force-coupon':
            lot = self.subscription.lot

            if lot.private is True:
                self.request.session['has_private_subscription'] = \
                    str(self.subscription.pk)

            return redirect('public:hotsite', slug=self.event.slug)

        return redirect('public:hotsite-status', slug=self.event.slug)

    def get_person(self):
        """ Se usuario possui person """
        if not self.request.user.is_authenticated or self.person:
            return self.person
        else:
            try:
                self.person = self.request.user.person
            except (ObjectDoesNotExist, AttributeError):
                pass

        return self.person

    def subscriber_has_account(self, email):
        if self.request.user.is_authenticated:
            return True

        try:
            User.objects.get(email=email)
            return True

        except User.DoesNotExist:
            pass

        return False

    def get_transactions(self):
        if self.transactions:
            return self.transactions

        self.transactions = []

        all_transactions = Transaction.objects.filter(
            subscription=self.subscription,
            lot=self.subscription.lot)

        now = datetime.now().date()

        for transaction in all_transactions:
            if transaction.boleto_expiration_date:
                if transaction.boleto_expiration_date > now:
                    self.transactions.append(transaction)
            else:
                self.transactions.append(transaction)

        return self.transactions

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

    def is_subscribed(self):
        """
            Se já estiver inscrito retornar True
        """
        user = self.request.user

        if user.is_authenticated:
            try:
                person = user.person
                subscription = Subscription.objects.get(person=person,
                                                        event=self.event)
                self.subscription = subscription
                return True

            except (Subscription.DoesNotExist, AttributeError):
                pass

        return False

    def is_private_event(self):
        """ Verifica se evento possui apenas lotes privados. """
        public_lots = []
        private_lots = []

        for lot in self.event.lots.all():
            if lot.private is True:
                private_lots.append(lot.pk)
                continue

            if self.is_lot_publicly_available(lot):
                public_lots.append(lot.pk)

        return len(public_lots) == 0 and len(private_lots) > 0

    @staticmethod
    def is_lot_publicly_available(lot):

        if lot.status == lot.LOT_STATUS_RUNNING and not lot.private:
            return True

        return False
