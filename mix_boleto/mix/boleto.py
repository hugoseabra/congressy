from datetime import datetime

from django.db.transaction import atomic

from hotsite.forms import PaymentForm
from mix_boleto.models import MixBoleto as MixBoletoModel, SyncBoleto
from payment.helpers.payment_helpers import amount_as_decimal
from payment.models import Transaction, TransactionStatus
from .connection import MixConnection, DatabaseError


class MixBoleto(object):
    """
    Sincroniza o estado de um boleto de inscrição na MixEvents junto a
    Congressy, gerando um registro de boleto equivalente.
    """

    def __init__(self,
                 id,
                 expiration_date,
                 amount,
                 installments,
                 installment_part,
                 created,
                 updated,
                 link_boleto=None,
                 id_caixa=None,
                 cancelled=False):

        self.id = id
        self.expiration_date = expiration_date
        self.amount = amount
        self.installments = installments
        self.installment_part = installment_part
        self.link_boleto = link_boleto
        self.created = created
        self.updated = updated
        self.id_caixa = id_caixa
        self.cancelled = cancelled

        self.boleto = None
        self.sync_boleto = None

        self.paid = False
        self.payment_date = None
        self.transaction = None

    def sync(self, db: MixConnection, mix_subscription):

        """
        CRITÉRIOS DE SINCRONIZAÇÃO:

        - O boleto da inscrição na MixEvents possui uma situação que deve
        refletir o boleto equivalmente na Congressy. Sendo assim, passaremos
        pelas seguinte verificações:

        Boleto já existe na Congressy através do MixBoleto?
        - Sim: boleto na MixEvents está cancelado:
            - Não: tudo certo;
            - Sim: cancelar boleto na Congressy pelo MixBoleto;
        - Não: criar registro de Boleto e sincronizar com transação com
        MixBoleto;
        """

        event_id = mix_subscription.mix_category.event_id

        with atomic():
            try:
                self.boleto = MixBoletoModel.objects.get(
                    sync_resource_id=db.sync_resource_id,
                    event_id=event_id,
                    mix_boleto_id=self.id,
                )

                if self.boleto.paid is True or self.boleto.cancelled is True:
                    return

            except MixBoletoModel.DoesNotExist:

                self.boleto = MixBoletoModel.objects.create(
                    sync_resource_id=db.sync_resource_id,
                    mix_boleto_id=self.id,
                    cgsy_subscription_id=mix_subscription.cgsy_subscription.pk,
                    event_id=event_id,
                    amount=self.amount,
                    installments=self.installments,
                    installment_part=self.installment_part,
                    cancelled=self.cancelled,
                    mix_created=self.created,
                    mix_updated=self.updated,
                )

            self._sync_boleto(db, mix_subscription)

        self.created = self.boleto.mix_created
        self.updated = self.boleto.mix_updated

    def _sync_boleto(self, db: MixConnection, mix_subscription):

        event_id = mix_subscription.mix_category.event_id

        try:
            # Se boleto está sincronizado
            self.sync_boleto = SyncBoleto.objects.get(
                mix_boleto_id=self.boleto.pk,
                event_id=event_id,
                mix_subscription_id=mix_subscription.mix_subscription_id,
            )

            # Se existe, vamos verificar a transação:
            try:
                self.transaction = Transaction.objects.get(
                    pk=self.sync_boleto.cgsy_transaction_id,
                )

                sync_to_mix = False

                if self.transaction.boleto_url:
                    self.link_boleto = self.transaction.boleto_url
                    sync_to_mix = True

                if self.transaction.status == Transaction.PAID and \
                        not self.id_caixa:
                    trans_status = TransactionStatus.objects.filter(
                        transaction_id=self.transaction.pk,
                        status=Transaction.PAID,
                    ).last()

                    self.payment_date = datetime.strptime(
                        trans_status.date_created,
                        "%Y-%m-%dT%H:%M:%S.%fZ"
                    )

                    self.paid = True
                    sync_to_mix = True

                if sync_to_mix is True:
                    self._sync_to_mix(db, mix_subscription)

            except Transaction.DoesNotExist:
                # sub = mix_subscription.cgsy_subscription
                # transaction = self._create_transaction(sub)
                pass

        except SyncBoleto.DoesNotExist:
            # Não sincronizado. Vamos criar a sincronização:
            # - Transação relacionada;
            # - Relacionar transação com MixBoleto através de SyncBoleto

            sub = mix_subscription.cgsy_subscription
            self.transaction = self._create_transaction(sub)

            self.sync_boleto = SyncBoleto.objects.create(
                mix_boleto=self.boleto,
                mix_subscription_id=mix_subscription.mix_subscription_id,
                cgsy_transaction_id=self.transaction.pk,
            )

    def _create_transaction(self, subscription):

        # form required prefix
        data = {
            'payment-transaction_type': Transaction.BOLETO,
            'payment-installments': self.installments,
            'payment-installment_part': self.installment_part,
            'payment-boleto_expiration_date': self.expiration_date,
            'payment-boleto_url': self.link_boleto,
            'payment-amount': self.amount,
            'payment-card_hash': None,
            'payment-lot_as_json': None,
        }

        form = PaymentForm(
            subscription=subscription,
            selected_lot=subscription.lot,
            data=data,
            prefix='payment'
        )
        valid = form.is_valid()

        if valid is False:
            raise Exception('PaymentForm not valid.')

        return form.save()

    def _sync_to_mix(self, db: MixConnection, mix_subscription):

        # Update boleto na MixEvents
        mix_insc_id = mix_subscription.mix_subscription_id

        try:

            db.connection.begin()

            if self.paid is True and not self.id_caixa:
                sub_sql = 'INSERT INTO caixa'
                sub_sql += ' (idinscricao, valorpago, pagamento, situacao,'
                sub_sql += ' tipo, obs, tid, transacao, _crdt)'
                sub_sql += ' VALUES ('
                sub_sql += '{}, {}, {}, 02, 01, "from Congressy", "", "", ' \
                           'now())'
                sql = sub_sql.format(
                    self.id,
                    amount_as_decimal(self.amount),
                    datetime.now().strftime("%Y%m%d")
                )

                self.id_caixa = db.insert(sql)

            sub_sql = "UPDATE boleto SET link_boleto='{}'".format(
                self.link_boleto
            )
            sql = sub_sql

            if self.id_caixa:
                sub_sql = ", idcaixa={}".format(self.id_caixa)
                sql += sub_sql

            sub_sql = " WHERE idboleto={} AND idinscricao={} AND parci = {}"
            sql += sub_sql.format(self.id, mix_insc_id, self.installment_part)

            db.update(sql)

        except DatabaseError as e:
            print(str(e))
            db.connection.rollback()
