from decimal import Decimal

from django import forms
from django.db.models import Sum

from payment_debt.models import Debt, Payment


class DebtForm(forms.ModelForm):
    class Meta:
        model = Debt
        fields = (
            'type',
            'status',
            'amount',
            'liquid_amount',
            'installments',
            'installment_amount',
            'installment_interests_amount',
        )

    def __init__(self, subscription, *args, **kwargs):
        self.subscription = subscription
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        self.instance.subscription = self.subscription
        return super().save(commit)


class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = (
            'cash_type',
            'amount',
        )

    def __init__(self, subscription, *args, **kwargs):
        self.subscription = subscription
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        self.instance.subscription = self.subscription
        instance = super().save(commit)

        self._update_debt_statuses()

        return instance

    def _update_debt_statuses(self):
        """
        Ao inserir ou atualizar um pagamento, deve-se processar o montante
        de pagamentos existentes equiparando-os com as pendẽncias existentes
        e atualizar os status das pendências.
        """
        payments_amount = self.subscription.payments.filter(
            paid=True
        ).aggregate(total=Sum('amount'))

        payments_amount = payments_amount['total'] or Decimal(0)

        # Se não há pagamentos, ignorar
        if not payments_amount:
            return

        debts_amount = subscription.debts.aggregate(total=Sum('amount'))
        debts_amount = debts_amount['total'] or Decimal(0)

        if payments_amount > debts_amount:
            # Número de pagamentos é maior do que as pendências. Então, vamos
            # Atualizar todas pendências como pagas e a pendência de inscrição
            # como CRÉDITO.

            # Todas pendências que não de inscrição estarão pagas.
            debts = subscription.debts.exclude(
                type=Debt.DEBT_TYPE_SUBSCRIPTION)
            for debt in debts:
                debt.status = Debt.DEBT_STATUS_PAID
                debt.save()

            # A pendência de inscriçãoe estará com crédito.
            sub_debt = \
                subscription.debts.filter(
                    type=Debt.DEBT_TYPE_SUBSCRIPTION).first()
            sub_debt.status = Debt.DEBT_STATUS_CREDIT
            sub_debt.save()

        if payments_amount == debts_amount:
            # Todas as pendências estão pagas. Atualiza pendências como PAGAS.
            for debt in subscription.debts.all():
                debt.status = Debt.DEBT_STATUS_PAID
                debt.save()

        if payments_amount < debts_amount:
            # Se há pagamento, mas as pendências são maiores, verificar se
            # alguma dos pagamentos cobre alguma das pendências.
            processed_payment_amount = payments_amount

            for debt in subscription.debts.all():
                if round(processed_payment_amount, 2) >= debt.amount:
                    debt.status = Debt.DEBT_STATUS_PAID
                    debt.save()
                    processed_payment_amount -= debt.amount


class ManualPaymentForm(PaymentForm):
    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        self.instance.paid = True
        self.instance.manual = True
        self.instance.manual_author = '{} ({})'.format(
            self.user.get_full_name(),
            self.user.email,
        )
        return super().save(commit)
