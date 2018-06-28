"""
    Formulário usado para pegar os dados de pagamento
"""

import logging

from django import forms
from django.db.transaction import atomic

from gatheros_event.locale import locales
from gatheros_event.models import Person
from gatheros_subscription.models import Lot, Subscription
from payment.exception import (
    TransactionApiError,
    TransactionDataError,
    TransactionError,
    TransactionMisconfiguredError,
)
from payment.helpers import (
    PagarmeDataBuilder,
    payment_helpers,
)
from payment.models import Transaction
from payment.tasks import create_pagarme_transaction
from payment_debt.forms import Debt, DebtForm

LOGGER = logging.getLogger(__name__)


class DebtAlreadyPaid(Exception):
    """
    Quando uma inscrição não é possível de ser feito porque a inscrição já
    está paga.
    """
    pass


class PagarMeCheckoutForm(forms.Form):
    subscription = forms.UUIDField(
        # widget=forms.HiddenInput(),
        required=True,
    )

    selected_lot = forms.IntegerField(
        # widget=forms.HiddenInput(),
        required=False,
    )

    transaction_type = forms.CharField(
        # widget=forms.HiddenInput(),
        required=True,
    )

    installments = forms.IntegerField(
        # widget=forms.HiddenInput(),
        required=False,
    )

    amount = forms.IntegerField(
        # widget=forms.HiddenInput(),
        required=True,
    )

    card_hash = forms.CharField(
        # widget=forms.HiddenInput(),
        required=False,
    )

    next_url = forms.CharField(
        # widget=forms.HiddenInput(),
        required=False,
    )

    class Media:
        js = (
            'https://assets.pagar.me/checkout/checkout.js',
            'assets/js/pagarme-checkout.js',
            'assets/js/pagarme-checkout-form.js',
        )

    def __init__(self, require_lot=False, **kwargs):

        self.subscription = None
        self.subscription_debt_form = None
        self.product_debt_forms = None
        self.service_debt_forms = None

        super().__init__(**kwargs)

        # Se lote deve ser selecionado externamente:
        if require_lot is True:
            self.fields['selected_lot'].required = True

    def clean_subscription(self):
        sub_pk = self.cleaned_data.get('subscription')
        try:
            self.subscription = Subscription.objects.get(pk=sub_pk)

            if self.subscription.free is True:
                msg = 'Pagamentos não podem ser processados para inscrições' \
                      ' gratuitas.'
                self.add_error(None, msg)
                raise forms.ValidationError(msg)

            person = self.subscription.person

            country = person.country
            if country == locales.BRASIL['codes']['digits_2']:
                if not person.cpf:
                    msg = 'Você não pode criar meio de pagamento para' \
                          ' inscrições de pessoas cujo CPF não foi informado.'
                    self.add_error(None, msg)
                    raise forms.ValidationError(msg)

                address_fields = (
                    'street',
                    # 'complement',
                    # 'number',
                    'village',
                    'zip_code',
                )

            else:
                if not person.international_doc:
                    msg = 'Você não pode criar meio de pagamento para' \
                          ' inscrições de pessoas cujo ID/Passport não foi' \
                          ' informado.'
                    self.add_error(None, msg)
                    raise forms.ValidationError(msg)

                address_fields = (
                    'street',
                    # 'complement',
                    # 'number',
                    'village',
                    'city_international',
                    'state_international',
                    'zip_code_international',
                )

            for f in address_fields:
                if not getattr(person, f):
                    msg = 'Você não pode criar meio de pagamento sem' \
                          ' informar o endereço completo.'
                    self.add_error(None, msg)
                    raise forms.ValidationError(msg)

        except Subscription.DoesNotExist:
            raise forms.ValidationError({
                forms.ALL_FIELDS: 'Inscrição não informada.'
            })

        return self.subscription

    def clean_selected_lot(self):
        lot_pk = self.cleaned_data.get('selected_lot')
        try:
            lot = Lot.objects.get(pk=lot_pk)

            # Caso a inscrição exista e o lote for diferente, altera o lote.
            self.subscription.lot = lot

        except Lot.DoesNotExist:
            lot = self.subscription.lot

        return lot

    def clean_transaction_type(self):
        transaction_type = self.cleaned_data['transaction_type']

        boleto_allowed = payment_helpers.is_boleto_allowed(
            self.subscription.event
        )

        if transaction_type == Transaction.BOLETO:
            if boleto_allowed is False:
                msg = 'Transação com boleto não é permitida.'
                self.add_error(None, msg)
                raise forms.ValidationError(msg)

            open_boletos = payment_helpers.get_opened_boleto_transactions(
                self.subscription
            )
            if open_boletos.count() > 0:
                msg = 'Já existe um ou mais boletos em aberto para esta' \
                      ' inscrição.'

                self.add_error(None, msg)
                raise forms.ValidationError(msg)

        return transaction_type

    def clean_installments(self):
        installments = self.cleaned_data['installments']
        if not installments or int(installments) <= 1:
            return 1

        return int(installments)

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if not amount:
            return amount

        return payment_helpers.amount_as_decimal(amount)

    def clean_card_hash(self):
        card_hash = self.cleaned_data['card_hash']
        return card_hash or None

    def clean(self):
        cleaned_data = super().clean()

        self.subscription_debt_form = self._create_subscription_debt_form()
        self.product_debt_forms = self._create_product_debt_forms()
        self.service_debt_forms = self._create_service_debt_forms()

        if not self.subscription_debt_form.is_valid():
            error_msgs = []
            for field, errs in self.subscription_debt_form.errors.items():
                error_msgs.append(str(errs))

            raise forms.ValidationError(
                'Dados de pendência inválidos: {}'.format("".join(error_msgs))
            )

        for debt_form in self.product_debt_forms:
            if not debt_form.is_valid():
                error_msgs = []
                for field, errs in debt_form.items():
                    error_msgs.append(str(errs))

                raise forms.ValidationError(
                    'Dados de pendência de opcionais inválidos:'
                    ' {}'.format("".join(error_msgs))
                )

        for debt_form in self.service_debt_forms:
            if not debt_form.is_valid():
                error_msgs = []
                for field, errs in debt_form.items():
                    error_msgs.append(str(errs))

                raise forms.ValidationError(
                    'Dados de pendência de atividades extras inválidos:'
                    ' {}'.format("".join(error_msgs))
                )

        return cleaned_data

    def save(self):
        with atomic():
            self.subscription.save()

            # Novo ou edição de pendência financeira
            sub_debt = self.subscription_debt_form.save()

            try:
                # Construção de dados para transaçao do Pagarme
                builder = PagarmeDataBuilder(subscription=self.subscription)

                builder.add_debt(sub_debt)

                for debt_form in self.service_debt_forms:
                    serv_debt = debt_form.save()
                    builder.add_debt(serv_debt)

                for debt_form in self.product_debt_forms:
                    prod_debt = debt_form.save()
                    builder.add_debt(prod_debt)

                # Cria transação.
                create_pagarme_transaction(
                    subscription=self.subscription,
                    data=builder.build(
                        amount=self.cleaned_data.get('amount'),
                        transaction_type=self.cleaned_data.get(
                            'transaction_type'
                        ),
                        installments=self.cleaned_data.get('installments'),
                        card_hash=self.cleaned_data.get('card_hash'),
                    )
                )

            except TransactionDataError as e:
                LOGGER.error(
                    'Um erro aconteceu enquanto se tentava construir os dados'
                    ' de uma transação. Detalhes: {}'.format(e)
                )
                raise TransactionError(
                    'Erro interno ao realizar transação. A equipe técnica já'
                    ' foi informa e este erro será resolvido dentro de alguns'
                    ' minutos.'
                )

            except TransactionMisconfiguredError as e:
                LOGGER.warning(
                    'O evento "{}" não pode realizar transações não pode'
                    ' completar uma transação para a inscrição "{}".'
                    ' Detalhes: {}'.format(
                        '{} ({})'.format(
                            self.subscription.event.name,
                            self.subscription.event.pk,
                        ),
                        '{} ({})'.format(
                            self.subscription.person.name,
                            self.subscription.pk,
                        ),
                        str(e)
                    )
                )
                raise TransactionError(
                    'O evento não pode realizar transações. Por favor,'
                    ' entre em contato com o organizador do evento informando'
                    ' sobre o ocorrido.'
                )

            except TransactionApiError as e:
                LOGGER.error(
                    'Um erro aconteceu enquanto se tentava realizar uma'
                    ' transação. Detalhes: {}'.format(e)
                )
                raise TransactionError(str(e))

            except TransactionError as e:
                raise e

    def _create_subscription_debt_form(self):
        """ Cria formulário de pendência financeira de inscrição. """

        debt_kwargs = {
            'subscription': self.subscription,
            'data': {
                'name': 'Inscrição: {} ({})'.format(
                    self.subscription.event.name,
                    self.subscription.pk,
                ),
                'item_id': str(self.subscription.pk),
                'amount': self.subscription.lot.get_calculated_price(),
                'installments': self.cleaned_data.get('installments', 1),
                'status': Debt.DEBT_STATUS_DEBT,
                'type': Debt.DEBT_TYPE_SUBSCRIPTION,
            }
        }

        try:
            debt = self.subscription.debts.get(
                type=Debt.DEBT_TYPE_SUBSCRIPTION,
                subscription=self.subscription,
                status=Debt.DEBT_STATUS_DEBT,
            )

            debt_kwargs['instance'] = debt

        except Debt.DoesNotExist:
            pass

        return DebtForm(**debt_kwargs)

    def _create_service_debt_forms(self):
        """ Cria formulário de pendência financeira de atividade extra. """

        services = self.subscription.subscription_services.all()

        service_forms = []
        for service in services:
            if not service.optional_price:
                continue

            debt_kwargs = {
                'subscription': self.subscription,
                'data': {
                    'name': 'Atividade extra: {} ({})'.format(
                        service.optional.name,
                        service.optional.pk,
                    ),
                    'item_id': str(service.optional.pk),
                    'amount': service.optional.price,
                    # parcelamento sempre 1
                    'installments': 1,
                    'status': Debt.DEBT_STATUS_DEBT,
                    'type': Debt.DEBT_TYPE_SERVICE,
                }
            }

            try:
                debt = self.subscription.debts.get(
                    type=Debt.DEBT_TYPE_SERVICE,
                    subscription=self.subscription,
                    status=Debt.DEBT_STATUS_DEBT,
                )

                debt_kwargs['instance'] = debt

            except Debt.DoesNotExist:
                pass

            service_forms.append(DebtForm(**debt_kwargs))

        return service_forms

    def _create_product_debt_forms(self):
        """ Cria formulário de pendência financeira de opcionais. """

        products = self.subscription.subscription_products.all()

        prod_forms = []
        for product in products:
            if not product.optional_price:
                continue

            debt_kwargs = {
                'subscription': self.subscription,
                'data': {
                    'name': 'Atividade extra: {} ({})'.format(
                        product.optional.name,
                        product.optional.pk,
                    ),
                    'item_id': str(product.optional.pk),
                    'amount': product.optional.price,
                    # parcelamento sempre 1
                    'installments': 1,
                    'status': Debt.DEBT_STATUS_DEBT,
                    'type': Debt.DEBT_TYPE_PRODUCT,
                }
            }

            try:
                debt = self.subscription.debts.get(
                    type=Debt.DEBT_TYPE_PRODUCT,
                    subscription=self.subscription,
                    status=Debt.DEBT_STATUS_DEBT,
                )

                debt_kwargs['instance'] = debt

            except Debt.DoesNotExist:
                pass

            prod_forms.append(DebtForm(**debt_kwargs))

        return prod_forms
