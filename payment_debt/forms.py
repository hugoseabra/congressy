from decimal import Decimal

from django import forms

from payment_debt.models import Debt
from payment.helpers import payment_helpers

class DebtForm(forms.ModelForm):
    class Meta:
        model = Debt
        fields = (
            'type',
            'status',
            'amount',
            'installments',
        )

    def __init__(self, subscription, *args, **kwargs):
        self.subscription = subscription

        # O valor líquido é quanto o organizador irá receber, que pode variar
        # de acordo com a configuração do lote da inscrição.
        self.liquid_amount = None

        # montante a ser pago originalmente. O montante vindo de 'data' pode
        # não ser o mesmo. Se houver parcelamento, a diferença são dos juros
        # de parcelamento. Se não houver, o formulári deve ser invalidado.
        self.original_amount = None

        # Montante a ser pego por parcela;
        self.installment_amount = Decimal(0)

        # Valor de juros a ser pago ao final das parcelas.
        self.installment_interests_amount = Decimal(0)

        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()

        if self.subscription.free is True:
            raise forms.ValidationError(
                'Pagamentos não podem ser processados para inscrições'
                ' gratuitas.'
            )

        # Calcula valor líquido.
        self._set_lot_amounts()
        self._set_installments_amount()
        self._set_installment_interests_amount()

        return cleaned_data

    def clean_installments(self):
        return int(self.cleaned_data.get('installments', 1) or 1)

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        amount = payment_helpers.amount_as_decimal(amount)

        if self._is_valid_amount() is False:
            raise forms.ValidationError(
                'Valor a ser processado no pagamento é diferente do valor'
                ' esperado.'
            )

        return amount

    def save(self, commit=True):
        self.instance.subscription = self.subscription
        self.instance.liquid_amount = self.liquid_amount
        self.instance.installments_amount = self.installment_amount
        self.instance.installment_interests_amount = \
            self.installment_interests_amount

        return super().save(commit)

    def _set_lot_amounts(self):
        """
        Seta valores líquidos e a ser pago esperados de acordo com a
        configuração do lote.
        """
        event = self.subscription.event
        lot = self.subscription.lot

        cgsy_percent = Decimal(event.congressy_percent) / 100
        percent_amount = lot.price * cgsy_percent

        if lot.transfer_tax is True:
            # Se há transferência de taxas ao participante, o valor a ser
            # recebido pelo organizador será o valor informando em 'price'.
            # O montante a processar o pagamento possui as taxas adicionais.
            self.liquid_amount = lot.price
            self.original_amount = round(lot.price + percent_amount, 2)

        else:
            # Se não há transferência de taxas ao participante, o valor a ser
            # recebeido pelo organizador será o valor informado em 'price'
            # menos as taxas adicionais. O montante a processar é o valor
            # original de 'price'.
            self.original_amount = lot.price
            self.liquid_amount = round(lot.price - percent_amount, 2)

    def _is_valid_amount(self):
        """ Valida se o montante informado é válido. """
        amount = payment_helpers.amount_as_decimal(self.data.get('amount'))
        if not amount:
            return False

        if not self.original_amount:
            self._set_lot_amounts()

        installments = self.cleaned_data.get('installments', 1) or 1

        if int(installments) <= 1:
            return self.original_amount == Decimal(amount)

        return True

    def _set_installments_amount(self):
        """ Seta montante por parcela. """
        installments = self.cleaned_data.get('installments', 1)

        if self._is_valid_amount() is False:
            self.installment_amount = Decimal(0)
            return

        if installments <= 1:
            self.installment_amount = self.original_amount
            return

        self.installment_amount = Decimal(amount) / installments

    def _set_installment_interests_amount(self):
        """ Seta valor de juros a ser pago ao final de todas as parcelas. """
        if self._is_valid_amount() is False:
            self.installment_interests_amount = Decimal(0)
            return

        amount = payment_helpers.amount_as_decimal(self.data.get('amount'))
        installments = self.cleaned_data.get('installments', 1)

        if installments <= 1:
            # Sem parcelamento, sem juros.
            self.installment_interests_amount = Decimal(0)
            return

        if not self.installment_amount:
            self._set_installments_amount()

        total_amount = self.installment_amount * installments

        self.installment_interests_amount = round((amount / total_amount), 2)
