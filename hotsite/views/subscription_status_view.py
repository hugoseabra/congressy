"""
    View usada para verificar o status da sua inscrição
"""

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import redirect
from django.views import generic

from gatheros_subscription.models import Subscription
from hotsite.views import EventMixin
from payment.models import Transaction


class SubscriptionStatusView(EventMixin, generic.TemplateView):
    template_name = 'hotsite/subscription_status.html'
    person = None
    subscription = None

    def dispatch(self, request, *args, **kwargs):

        response = super().dispatch(request, *args, **kwargs)

        self.person = self.get_person()

        # Se  não há lotes pagos, não há o que fazer aqui.
        if not self.has_paid_lots():
            return redirect(
                'public:hotsite',
                slug=self.event.slug
            )

        if not request.user.is_authenticated or not self.person:
            return redirect('public:hotsite', slug=self.event.slug)

        try:
            self.subscription = Subscription.objects.get(
                event=self.event, person=self.person, completed=True)

        except Subscription.DoesNotExist:
            messages.error(
                message='Você não possui inscrição neste evento.',
                request=request
            )
            return redirect('public:hotsite', slug=self.event.slug)

        return response

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        context['person'] = self.get_person()
        context['is_subscribed'] = self.is_subscribed()
        context['transactions'] = self.get_transactions()
        context['allow_transaction'] = self.get_allowed_transaction()
        context['pagarme_key'] = settings.PAGARME_ENCRYPTION_KEY
        context['remove_preloader'] = True
        context['subscription'] = self.subscription

        return context

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

        try:
            transactions = Transaction.objects.filter(
                subscription=self.subscription)
        except Transaction.DoesNotExist:
            return False

        return transactions

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
                                                        completed=True,
                                                        event=self.event)
                self.subscription = subscription
                return True

            except (Subscription.DoesNotExist, AttributeError):
                pass

        return False
