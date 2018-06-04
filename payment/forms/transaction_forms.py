from datetime import datetime

from django import forms

from core.forms import PriceInput
from gatheros_subscription.helpers import report_payment
from payment.models import Transaction


class ManualTransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = (
            'amount',
            'manual_payment_type',
            'manual_author',
        )
        widgets = {
            'amount': PriceInput(
                attrs={'data-mask': '#.##0,00', 'data-mask-reverse': 'true'}
            )
        }

    def __init__(self, subscription, *args, **kwargs):
        self.subscription = subscription
        super().__init__(*args, **kwargs)

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if not amount:
            raise forms.ValidationError('Você deve informar um valor.')

        return amount

    def save(self, commit=True):

        self.instance.subscription = self.subscription
        self.instance.lot = self.subscription.lot
        self.instance.lot_price = self.subscription.lot.get_calculated_price()

        self.instance.manual = True
        self.instance.date_created = datetime.now()
        self.instance.type = Transaction.MANUAL
        self.instance.status = Transaction.PAID
        self.instance.liquid_amount = self.instance.amount

        instance = super().save(commit=commit)

        calculator = report_payment.PaymentReportCalculator(
            subscription=self.subscription
        )

        if calculator.is_subscription_confirmed:
            self.subscription.status = self.subscription.CONFIRMED_STATUS
        else:
            self.subscription.status = self.subscription.AWAITING_STATUS

        self.subscription.save()

        return instance
