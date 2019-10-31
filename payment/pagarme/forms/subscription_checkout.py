"""
    Formulário usado para pegar os dados de pagamento
"""

import logging
import uuid

from django import forms
from django.db.models import ObjectDoesNotExist
from django.db.transaction import atomic

from gatheros_subscription.models import Subscription
from installment.models import Part
from payment.exception import (
    TransactionApiError,
    TransactionDataError,
    TransactionError,
    TransactionMisconfiguredError,
)
from payment.models import Benefactor, Transaction, Payer
from payment.pagarme.transaction.builder import SubscriptionTransactionBuilder
from payment.pagarme.transaction.service import PagarmeAPISubscriptionService
from payment.pagarme.transaction.transaction import PagarmeTransaction
from payment_debt.forms import DebtForm
from payment_debt.models import Debt
from .mixins import CheckoutValidationForm

LOGGER = logging.getLogger(__name__)


class SubscriptionCheckoutForm(CheckoutValidationForm):
    subscription_pk = forms.UUIDField(
        required=True,
        widget=forms.HiddenInput(),
    )

    benefactor_pk = forms.IntegerField(
        required=False,
        widget=forms.HiddenInput(),
    )

    def __init__(self, *args, **kwargs):
        self.subscription_instance = None
        self.event_instance = None

        self.person = None
        self.lot_instance = None

        self.subscription_debt_form = None
        self.product_debt_forms = list()
        self.service_debt_forms = list()

        super().__init__(*args, **kwargs)

    def clean_subscription_pk(self):
        subscription_pk = self.cleaned_data.get('subscription_pk')

        if not subscription_pk:
            raise forms.ValidationError('Inscrição não informada.')

        if not self.event_instance:
            return subscription_pk

        try:
            self.subscription_instance = Subscription.objects.get(
                pk=subscription_pk,
                event_id=self.event_instance.pk,
            )
            self.person = self.subscription_instance.person
            self.lot_instance = self.subscription_instance.lot

        except Subscription.DoesNotExist:
            raise forms.ValidationError('Inscrição não existe.')

        return subscription_pk

    def clean_benefactor_pk(self):

        benefactor_pk = self.cleaned_data.get('benefactor_pk')

        if not self.subscription_instance:
            return benefactor_pk

        if benefactor_pk:
            person_pk = self.subscription_instance.person_id

            try:
                self.benefactor_instance = Benefactor.objects.get(
                    pk=benefactor_pk,
                    beneficiary_id=person_pk,
                )

            except Benefactor.DoesNotExist:
                raise forms.ValidationError('Possível pagador não existe')

        return benefactor_pk

    def save(self, *_, **__):
        with atomic():
            self.subscription_instance.save()

            # Novo ou edição de pendência financeira
            self.subscription_debt_form.save()

            for debt_form in self.service_debt_forms:
                debt_form.save()

            for debt_form in self.product_debt_forms:
                debt_form.save()

        try:
            interests_amount = self.cleaned_data.get('interests_amount')
            amount_to_transact = self.amount_to_transact

            if interests_amount and interests_amount > 0:
                amount_to_transact += interests_amount

            builder = self._create_builder(
                payer=self.payer_instance,
                liquid_amount=self.liquid_amount,
                is_company=self.payer_is_company,
            )

            transaction_type = self.cleaned_data['transaction_type']
            lot_id = self.subscription_instance.lot_id

            if transaction_type == Transaction.BOLETO:

                if self.installment_part_instance:
                    exp_date = \
                        self.installment_part_instance.expiration_date

                else:
                    exp_date = \
                        self.cleaned_data.get('boleto_expiration_date') or None

                builder.set_as_boleto(expiration_date=exp_date)

                # Se existe boleto aberta com o mesmo valor.
                try:
                    transaction_filter = {
                        'amount': amount_to_transact,
                        'liquid_amount': self.liquid_amount,
                        'lot_id': lot_id,
                        'type': Transaction.BOLETO,
                        'status': Transaction.WAITING_PAYMENT,
                        # 'admin_cancelled': False,
                    }

                    if self.installment_part_instance:
                        transaction_filter['part_id'] = \
                            self.installment_part_instance.pk

                    if isinstance(self.payer_instance, Benefactor):
                        transaction_filter['payer__benefactor_id'] = \
                            self.payer_instance.pk
                        transaction_filter['payer__subscription_id'] = \
                            self.subscription_instance.pk

                    transaction = \
                        self.subscription_instance.transactions.get(
                            **transaction_filter
                        )

                    return transaction

                except ObjectDoesNotExist:
                    pass

            elif transaction_type == Transaction.CREDIT_CARD:

                builder.set_as_credit_card(self.cleaned_data['card_hash'])

                # Se existe par aberta com o mesmo valor.
                try:
                    transaction = \
                        self.subscription_instance.transactions.get(
                            amount=amount_to_transact + interests_amount,
                            liquid_amount=self.liquid_amount,
                            lot_id=lot_id,
                            type=Transaction.CREDIT_CARD,
                            status=Transaction.PROCESSING,
                            # admin_cancelled=False,
                        )

                    return transaction

                except ObjectDoesNotExist:
                    pass

            builder.build()

            # Cria transação.
            pagarme_service = PagarmeAPISubscriptionService(
                pagarme_transaction=builder.pagarme_transaction,
                subscription=self.subscription_instance,
            )

            transaction = pagarme_service.create_transaction(
                num_installment_part=self.cleaned_data.get(
                    'installment_part',
                    1
                ),
                installment_interests_amount=self.cleaned_data.get(
                    'interests_amount'
                ),
                contract_part=self.installment_part_instance,
            )

            if self.benefactor_instance:
                Payer.objects.create(
                    subscription=self.subscription_instance,
                    benefactor=self.benefactor_instance,
                    transaction=transaction,
                )

            return transaction

        except TransactionDataError as e:
            LOGGER.error(
                'Um erro aconteceu enquanto se tentava construir os dados'
                ' de uma transação. Detalhes: {}'.format(e)
            )
            raise TransactionError(
                'Erro interno ao realizar transação. A equipe técnica já'
                ' foi informada e este erro será resolvido dentro de'
                ' alguns minutos.'
            )

        except TransactionMisconfiguredError as e:
            person = self.subscription_instance.person

            LOGGER.warning(
                'O evento "{}" não pode realizar transações não pode'
                ' completar uma transação para a inscrição "{}".'
                ' Detalhes: {}'.format(
                    '{} ({})'.format(
                        self.event_instance.name,
                        self.event_instance.pk,
                    ),
                    '{} ({})'.format(
                        person.name,
                        self.subscription_instance.pk,
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

    def _set_installment_data(self):
        if not self.subscription_instance:
            return

        part_pk = self.cleaned_data.get('installment_part_pk')

        if not part_pk:
            return

        try:
            part = Part.objects.get(
                pk=part_pk,
                contract__subscription_id=self.subscription_instance.pk,
                paid=False,
            )
            self.installment_part_instance = part
            self.installment_contract = part.contract

        except Part.DoesNotExist:
            raise self.add_error(
                'installment_part_pk',
                "Parcela pendente '{}' não encontrada nesta"
                " inscrição.".format(part_pk)
            )

    def _set_amount_to_transact(self):

        self.subscription_debt_form = self._create_subscription_debt_form()

        if not self.subscription_debt_form.is_valid():
            error_msgs = []
            for field, errs in self.subscription_debt_form.errors.items():
                error_msgs.append(str(errs))

            raise forms.ValidationError(
                'Dados de pendência inválidos: {}'.format("".join(error_msgs))
            )

        self.amount_to_transact = self.subscription_debt_form.amount
        self.liquid_amount = self.subscription_debt_form.liquid_amount

        self.product_debt_forms = self._create_product_debt_forms()

        for debt_form in self.product_debt_forms:
            if not debt_form.is_valid():
                error_msgs = []
                for field, errs in debt_form.items():
                    error_msgs.append(str(errs))

                raise forms.ValidationError(
                    'Dados de pendência de opcionais inválidos:'
                    ' {}'.format("".join(error_msgs))
                )

            self.amount_to_transact += debt_form.amount
            self.liquid_amount += debt_form.liquid_amount

        self.service_debt_forms = self._create_service_debt_forms()

        for debt_form in self.service_debt_forms:
            if not debt_form.is_valid():
                error_msgs = []
                for field, errs in debt_form.items():
                    error_msgs.append(str(errs))

                raise forms.ValidationError(
                    'Dados de pendência de atividades extras inválidos:'
                    ' {}'.format("".join(error_msgs))
                )

            self.amount_to_transact += debt_form.amount
            self.liquid_amount += debt_form.liquid_amount

    def _create_builder_instance(self, payer, is_company, liquid_amount):
        # Construção de dados para transação do Pagarme

        transaction = PagarmeTransaction(
            transaction_id=str(uuid.uuid4()),
            payment_method=self.cleaned_data.get('transaction_type'),
            interests_amount=self.cleaned_data.get('interests_amount'),
            installments=self.cleaned_data.get('num_installments'),
        )

        return SubscriptionTransactionBuilder(
            pagarme_transaction=transaction,
            subscription=self.subscription_instance,
            installment_part=self.installment_part_instance,
        )

    def _set_payer_instance(self):

        if self.benefactor_instance:
            self.payer_instance = self.benefactor_instance
            self.payer_is_company = self.benefactor_instance.is_company
        else:
            self.payer_is_company = False
            self.payer_instance = self.subscription_instance.person

    def _create_subscription_debt_form(self):
        """ Cria formulário de pendência financeira de inscrição. """

        debt_kwargs = {
            'subscription': self.subscription_instance,
            'data': {
                'name':
                    'Inscrição: {}, Ingresso: {} ({})'.format(
                        self.subscription_instance.code,
                        self.subscription_instance.lot.name[:10],
                        self.subscription_instance.lot_id,
                    ),
                'item_id': str(self.subscription_instance.lot_id),
                'installments': self.cleaned_data.get('num_installments'),
                'status': Debt.DEBT_STATUS_DEBT,
                'type': Debt.DEBT_TYPE_SUBSCRIPTION,
            }
        }

        try:
            debt = self.subscription_instance.debts.get(
                type=Debt.DEBT_TYPE_SUBSCRIPTION,
                subscription=self.subscription_instance,
                status=Debt.DEBT_STATUS_DEBT,
            )

            debt_kwargs['instance'] = debt

            # # Se é possível processar pendência, somente débito não estiver
            # # pago e não possuindo crédito.
            # debt_allowed = debt.paid is False and debt.has_credit is False
            #
            # if debt_allowed is False:
            #     # Pendência financeira já está paga ou com crédito.
            #     raise DebtAlreadyPaid(
            #         'Esta pendência já está paga. Não é necessário realizar'
            #         ' novo registro de pendência.'
            #     )

        except Debt.DoesNotExist:
            pass

        return DebtForm(**debt_kwargs)

    def _create_service_debt_forms(self):
        """ Cria formulário de pendência financeira de atividade extra. """

        services = self.subscription_instance.subscription_services.all()

        service_forms = []
        for service in services:
            optional = service.optional

            if not optional.price:
                continue

            debt_kwargs = {
                'subscription': self.subscription_instance,
                'data': {
                    'name': 'Atividade extra: {} ({})'.format(
                        optional.name,
                        optional.pk,
                    ),
                    'item_id': str(optional.pk),
                    'installments': self.cleaned_data.get('num_installments'),
                    'status': Debt.DEBT_STATUS_DEBT,
                    'type': Debt.DEBT_TYPE_SERVICE,
                }
            }

            try:
                debt = self.subscription_instance.debts.get(
                    type=Debt.DEBT_TYPE_SERVICE,
                    item_id=str(optional.pk),
                )

                debt_kwargs['instance'] = debt

            except Debt.DoesNotExist:
                pass

            service_forms.append(DebtForm(**debt_kwargs))

        return service_forms

    def _create_product_debt_forms(self):
        """ Cria formulário de pendência financeira de opcionais. """

        products = self.subscription_instance.subscription_products.all()

        prod_forms = []
        for product in products:
            optional = product.optional

            if not optional.price:
                continue

            debt_kwargs = {
                'subscription': self.subscription_instance,
                'data': {
                    'name': 'Produto/Serviço: {} ({})'.format(
                        optional.name,
                        optional.pk,
                    ),
                    'item_id': str(optional.pk),
                    'installments': self.cleaned_data.get('num_installments'),
                    'status': Debt.DEBT_STATUS_DEBT,
                    'type': Debt.DEBT_TYPE_PRODUCT,
                }
            }

            try:
                debt = self.subscription_instance.debts.get(
                    type=Debt.DEBT_TYPE_PRODUCT,
                    item_id=str(optional.pk),
                )

                debt_kwargs['instance'] = debt

            except Debt.DoesNotExist:
                pass

            prod_forms.append(DebtForm(**debt_kwargs))

        return prod_forms
