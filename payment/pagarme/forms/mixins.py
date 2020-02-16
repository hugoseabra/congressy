"""
    Formulário usado para pegar os dados de pagamento
"""

import logging
from datetime import datetime
from decimal import Decimal

from django import forms

from core.util.string import clear_string
from gatheros_event.models import Event
from payment.helpers import (
    payment_helpers,
)
from payment.models import Benefactor, Transaction

LOGGER = logging.getLogger(__name__)


class CheckoutValidationForm(forms.Form):
    event_pk = forms.CharField(
        widget=forms.HiddenInput(),
        required=True,
    )

    transaction_type = forms.CharField(
        widget=forms.HiddenInput(),
        required=True,
    )

    # Quantidade de parcelas
    num_installments = forms.IntegerField(
        widget=forms.HiddenInput(),
        required=False,
    )

    # Numero da parcela
    installment_part_pk = forms.IntegerField(
        widget=forms.HiddenInput(),
        required=False,
    )

    # Valor devido íntegro sem taxas de parcelamento
    interests_amount = forms.DecimalField(
        decimal_places=2,
        max_digits=11,
        required=False,
    )

    boleto_expiration_date = forms.DateField(
        required=False,
        widget=forms.HiddenInput(),
        input_formats=[
            '%Y-%m-%d',
            '%d/%m/%Y',
            '%d/%m/%y',
        ]
    )

    card_number = forms.CharField(
        widget=forms.HiddenInput(),
        required=False,
    )

    card_cvv = forms.CharField(
        widget=forms.HiddenInput(),
        required=False,
    )

    card_expiration_date = forms.CharField(
        widget=forms.HiddenInput(),
        required=False,
    )

    card_holder_name = forms.CharField(
        widget=forms.HiddenInput(),
        required=False,
    )

    card_hash = forms.CharField(
        widget=forms.HiddenInput(),
        required=False,
    )

    def __init__(self, *args, **kwargs):
        self.event_instance = None

        self.benefactor_instance = None

        self.installment_contract = None
        self.installment_part_instance = None

        # Valor a transacionar
        self.amount_to_transact = Decimal(0)

        # Valor de juros (possívelmente de parcelamento)
        self.interests_amount = Decimal(0)

        # Valor destinado ao organizador.
        self.liquid_amount = Decimal(0)

        self.payer_instance = None
        self.payer_is_company = None

        super().__init__(*args, **kwargs)

    def clean_event_pk(self):
        event_pk = self.cleaned_data.get('event_pk')

        if not event_pk:
            raise forms.ValidationError('O evento deve ser informado.')

        try:
            self.event_instance = Event.objects.get(pk=event_pk)

        except Event.DoesNotExist:
            raise forms.ValidationError('Evento não encontrado.')

        return event_pk

    def clean_transaction_type(self):
        transaction_type = self.cleaned_data.get('transaction_type')
        allowed_types = (Transaction.CREDIT_CARD, Transaction.BOLETO,)

        if not self.event_instance:
            return transaction_type

        if transaction_type not in allowed_types:
            raise forms.ValidationError('Tipo de transação inválida.')

        boleto_allowed = payment_helpers.is_boleto_allowed(self.event_instance)

        if transaction_type == Transaction.BOLETO and boleto_allowed is False:
            raise forms.ValidationError(
                'Transação com boleto não é permitida.'
            )

        return transaction_type

    def clean_num_installments(self):
        num_installments = self.cleaned_data.get('num_installments')

        if not num_installments or int(num_installments) <= 1:
            num_installments = 1

        if num_installments > 10:
            num_installments = 10

        return int(num_installments)

    def clean_interests_amount(self):
        interests_amount = self.cleaned_data.get('interests_amount')

        if not interests_amount:
            return Decimal(0)

        return payment_helpers.amount_as_decimal(interests_amount)

    def clean_boleto_expiration_date(self):
        exp_date = self.cleaned_data.get('boleto_expiration_date')

        if not exp_date:
            return exp_date

        today = datetime.now().date()
        if exp_date < today:
            raise forms.ValidationError('A data de vencimento do boleto é'
                                        ' anterior à data atual.')

        return exp_date

    def clean(self):
        cleaned_data = super().clean()

        transaction_type = self.cleaned_data.get('transaction_type')

        if transaction_type == Transaction.CREDIT_CARD:
            if not self.cleaned_data.get('card_hash'):
                card_data = list(filter(None, [
                    self.cleaned_data.get('card_number'),
                    self.cleaned_data.get('card_cvv'),
                    self.cleaned_data.get('card_expiration_date'),
                    self.cleaned_data.get('card_holder_name'),
                ]))
                if len(card_data) < 4:
                    raise forms.ValidationError(
                        'Para transações de cartão você deve informar o'
                        ' card_hash ou dados do cartão.'
                    )

        if not self.errors:
            self._set_installment_data()
            self._set_payer_instance()

        self._set_amount_to_transact()
        self._set_interests_amount()

        if self.amount_to_transact <= 0:
            raise forms.ValidationError(
                'Não é possível realizar pagamento sem valor.'
            )

        return cleaned_data

    def _create_customer_data(self, payer, is_company):
        customer_data = {
            'external_id': str(payer.pk),
            'name': payer.name,
            'email': payer.email,
            'country': payer.country.lower(),
        }

        if payer.phone:
            customer_data['phones'] = [clear_string(
                payer.get_phone_display(),
                exclude_list=['+'],
            )]

        if is_company is True:
            if payer.country.lower() == 'br':
                customer_data['doc_type'] = 'cnpj'
                customer_data['doc_number'] = str(payer.cnpj).zfill(14)

            else:
                customer_data['doc_type'] = payer.doc_type
                customer_data['doc_number'] = payer.doc_number

        else:

            if payer.country.lower() == 'br':
                customer_data['doc_type'] = 'cpf'
                customer_data['doc_number'] = str(payer.cpf).zfill(11)

            else:
                customer_data['doc_type'] = payer.doc_type
                customer_data['doc_number'] = payer.doc_number

        return customer_data

    # noinspection PyMethodMayBeStatic
    def _create_billing_data(self, payer):
        billing_data = {
            'name': payer.name,
            'country': payer.country.lower(),
        }

        if payer.country.lower() == 'br':

            if payer.complement:
                payer.street += ', ' + payer.complement

            billing_data['street'] = payer.street

            billing_data['street_number'] = payer.number or 'S/N'
            billing_data['neighborhood'] = payer.village or ''
            billing_data['city'] = payer.city.name.lower().capitalize()
            billing_data['state'] = payer.city.uf.lower()
            billing_data['zipcode'] = payer.zip_code

        else:
            if payer.complement:
                payer.address_international += ', ' + payer.complement

            billing_data['street'] = payer.address_international

            billing_data['street_number'] = ''
            billing_data['neighborhood'] = ''
            billing_data['city'] = payer.city_international
            billing_data['state'] = payer.state_international
            billing_data['zipcode'] = payer.zip_code_international or '000'

        return billing_data

    def _create_builder(self, payer, is_company):

        builder = self._create_builder_instance()
        customer_data = self._create_customer_data(payer, is_company)

        builder.set_customer(**customer_data)

        if is_company is False:
            builder.pagarme_transaction.customer.set_as_individual(
                payer.birth_date
            )

        billing_data = self._create_billing_data(payer)
        builder.set_billing(**billing_data)

        return builder

    # ============= ABSTRACT METHODS ========================================

    def _set_payer_instance(self):
        raise NotImplementedError()

    def _set_amount_to_transact(self):
        raise NotImplementedError()

    def _set_interests_amount(self):
        raise NotImplementedError()

    def clean_benefactor_pk(self):
        raise NotImplementedError()

    def _set_installment_data(self):
        raise NotImplementedError()

    def _create_builder_instance(self):
        raise NotImplementedError()
