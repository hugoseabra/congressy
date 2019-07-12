from datetime import datetime

from django import forms

from core.forms import PriceInput
from gatheros_subscription.helpers import report_payment
from installment.models import Part
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

    paid = forms.BooleanField(
        initial=True,
        required=False,
    )

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

        # @Todo remover lot
        self.instance.ticket_lot = self.subscription.ticket_lot

        self.instance.manual = True
        self.instance.date_created = datetime.now()
        self.instance.liquid_amount = self.instance.amount

        self.instance.lot_price = self.subscription.ticket_lot.get_subscriber_price()

        self.instance.type = Transaction.MANUAL

        if self.cleaned_data['paid'] is True:
            self.instance.status = Transaction.PAID
        else:
            self.instance.type = Transaction.MANUAL
            self.instance.status = Transaction.WAITING_PAYMENT

        instance = super().save(commit=commit)

        calculator = report_payment.PaymentReportCalculator(
            subscription=self.subscription
        )

        if calculator.is_subscription_confirmed and self.cleaned_data['paid'] \
                is True:
            self.subscription.status = self.subscription.CONFIRMED_STATUS
        else:
            self.subscription.status = self.subscription.AWAITING_STATUS

        self.subscription.save()

        return instance


class PartManualTransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = (
            'amount',
            'manual_payment_type',
            'manual_author',
        )
        widgets = {
            'amount': forms.HiddenInput(),
        }

    paid = forms.BooleanField(
        initial=True,
        required=False,
    )

    part = forms.IntegerField(
        required=True,
        widget=forms.HiddenInput(),
    )

    def __init__(self, subscription, *args, **kwargs):
        self.subscription = subscription
        super().__init__(*args, **kwargs)
        self.fields['manual_payment_type'].choices = \
            Transaction.MANUAL_PAYMENT_TYPES[:-1]

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if not amount:
            raise forms.ValidationError('Você deve informar um valor.')

        return amount

    def save(self, commit=True):

        self.instance.subscription = self.subscription

        self.instance.part = Part.objects.get(pk=self.cleaned_data['part'])
        self.instance.ticket_lot = self.subscription.ticket_lot
        self.instance.lot_price = \
            self.subscription.ticket_lot.get_subscriber_price()
        self.instance.manual = True
        self.instance.date_created = datetime.now()
        self.instance.liquid_amount = self.instance.amount

        self.instance.type = Transaction.MANUAL

        if self.cleaned_data['paid'] is True:
            self.instance.status = Transaction.PAID
        else:
            self.instance.type = Transaction.MANUAL
            self.instance.status = Transaction.WAITING_PAYMENT

        instance = super().save(commit=commit)

        calculator = report_payment.PaymentReportCalculator(
            subscription=self.subscription
        )

        if calculator.is_subscription_confirmed and self.cleaned_data['paid'] \
                is True:
            self.subscription.status = self.subscription.CONFIRMED_STATUS
        else:
            self.subscription.status = self.subscription.AWAITING_STATUS

        self.subscription.save()

        return instance
