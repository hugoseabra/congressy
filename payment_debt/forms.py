from decimal import Decimal

from django import forms
from django.conf import settings

from payment.installments import Calculator
from payment_debt.models import Debt


class DebtForm(forms.ModelForm):
    class Meta:
        model = Debt
        fields = (
            'name',
            'item_id',
            'type',
            'status',
            'installments',
        )

    def __init__(self, subscription, *args, **kwargs):
        self.subscription = subscription
        self.lot = subscription.lot

        self.amount = Decimal(0)

        # O valor líquido é quanto o organizador irá receber, que pode variar
        # de acordo com a configuração do lote da inscrição.
        self.liquid_amount = Decimal(0)

        # montante a ser pago originalmente. O montante vindo de 'data' pode
        # não ser o mesmo. Se houver parcelamento, a diferença são dos juros
        # de parcelamento. Se não houver, o formulári deve ser invalidado.
        self.original_amount = Decimal(0)

        # Montante a ser pego por parcela;
        self.installment_amount = Decimal(0)

        # Valor de juros a ser pago ao final das parcelas.
        self.installment_interests_amount = Decimal(0)

        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()

        # if self.subscription.free is True:
        #     raise forms.ValidationError(
        #         'Pagamentos não podem ser processados para inscrições'
        #         ' gratuitas.'
        #     )

        # Calcula valor líquido.
        debt_type = cleaned_data.get('type', Debt.DEBT_TYPE_SUBSCRIPTION)
        if debt_type == Debt.DEBT_TYPE_SUBSCRIPTION:
            self.original_amount = self.subscription.lot.get_calculated_price()
            self.liquid_amount = self.subscription.lot.get_liquid_price()

        elif debt_type == Debt.DEBT_TYPE_SERVICE:
            self._set_service_amounts()

        elif debt_type == Debt.DEBT_TYPE_PRODUCT:
            self._set_product_amounts()

        self.amount = self.original_amount

        self._set_amount_with_interests()
        self._set_installments_amount()

        return cleaned_data

    def clean_installments(self):
        return int(self.cleaned_data.get('installments', 1) or 1)

    def save(self, commit=True):
        self.instance.subscription = self.subscription
        self.instance.amount = self.original_amount
        self.instance.liquid_amount = self.liquid_amount
        self.instance.installment_amount = self.installment_amount
        self.instance.installment_interests_amount = \
            self.installment_interests_amount

        return super().save(commit)

    def _set_amount_with_interests(self):
        """
        Define valor final do pagamento de acordo com juros de parcelamento.
        """
        interests_rate = settings.CONGRESSY_INSTALLMENT_INTERESTS_RATE

        amount = self.amount

        calculator = Calculator(
            interests_rate=Decimal(interests_rate / 100),
            total_installments=10,
            free_installments=self.lot.num_install_interest_absortion,
        )
        amount_with_interests = calculator.get_installment_total_amount(
            amount=amount,
            installments=self.cleaned_data.get('installments'),
        )
        self.installment_interests_amount = \
            calculator.get_installment_interests_amount(
                amount=amount,
                installments=self.cleaned_data.get('installments')
            )

        self.amount = amount_with_interests

    def _set_service_amounts(self):
        """
        Seta valores líquidos e a ser pago esperados de acordo com a
        configuração do lote.
        """
        for sub_addon in self.subscription.subscription_services.filter(
                optional_id=self.cleaned_data.get('item_id')
        ):
            self.liquid_amount += sub_addon.optional.liquid_price
            self.original_amount += sub_addon.optional.price

    def _set_product_amounts(self):
        """
        Seta valores líquidos e a ser pago esperados de acordo com a
        configuração do lote.
        """
        for sub_addon in self.subscription.subscription_products.filter(
                optional_id=self.cleaned_data.get('item_id')
        ):
            self.liquid_amount += sub_addon.optional.liquid_price
            self.original_amount += sub_addon.optional.price

    def _set_installments_amount(self):
        """ Seta montante por parcela. """
        if not self.amount:
            self.installment_amount = Decimal(0.00)

        installments = self.cleaned_data.get('installments', 1)

        self.installment_amount = self.amount

        if installments > 1:
            self.installment_amount = self.amount / int(installments)
