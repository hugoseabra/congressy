from datetime import datetime

from hotsite.forms import PaymentForm
from mix_boleto.models import MixBoleto as MixBoletoModel, SyncBoleto
from payment.models import Transaction, TransactionStatus
from .connection import MixConnection, DatabaseError


class MixBoleto(object):
    """
    Sincroniza o estado de um boleto de inscrição na MixEvents junto a
    Congressy, gerando um registro de boleto equivalente.
    """

    def __init__(self,
                 id,
                 idcaixa,
                 expiration_date,
                 amount,
                 installments,
                 installment_part,
                 link_boleto,
                 created,
                 updated,
                 cancelled=False):

        self.id = id
        self.idcaixa = idcaixa
        self.expiration_date = expiration_date
        self.amount = amount
        self.installments = installments
        self.installment_part = installment_part
        self.link_boleto = link_boleto
        self.created = created
        self.updated = updated
        self.cancelled = cancelled

        self.boleto = None
        self.sync_boleto = None

        self.paid = False
        self.payment_date = None

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

        try:
            self.boleto = MixBoletoModel.objects.get(
                sync_resource_id=db.sync_resource_id,
                mix_boleto_id=self.id,
            )

            if self.boleto.paid is True or self.boleto.cancalled is True:
                return

        except MixBoletoModel.DoesNotExist:

            self.boleto = MixBoletoModel.objects.filter(
                sync_resource_id=db.sync_resource_id,
                mix_boleto_id=self.id,
                cgsy_subscription_id=mix_subscription.cgsy_subscription.pk,
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

        try:
            # Se boleto está sincronizado
            self.sync_boleto = SyncBoleto.objects.get(
                mix_boleto_id=self.id,
            )

            # Se existe, vamos verificar a transação:
            try:
                transaction = Transaction.objects.get(
                    pk=self.sync_boleto.cgsy_transaction_id,
                )

            except Transaction.DoesNotExist:
                sub = mix_subscription.cgsy_subscription
                transaction = self._create_transaction(sub)

            sync_to_mix = False

            if transaction.boleto_url:
                self.link_boleto = transaction.boleto_url
                sync_to_mix = True

            if transaction.status == Transaction.PAID:
                trans_status = TransactionStatus.objects.filter(
                    transaction_id=transaction.pk,
                ).last()

                self.payment_date = datetime.strptime(
                    trans_status.date_created,
                    "%Y-%m-%dT%H:%M:%S.%fZ"
                )

                self.paid = True
                sync_to_mix = True

            if sync_to_mix is True:
                self._sync_to_mix(db, mix_subscription)

        except SyncBoleto.DoesNotExist:
            # Não sincronizado. Vamos criar a sincronização:
            # - Transação relacionada;
            # - Relacionar transação com MixBoleto através de SyncBoleto

            sub = mix_subscription.cgsy_subscription
            transaction = self._create_transaction(sub)

            self.sync_boleto = SyncBoleto.objects.create(
                mix_boleto=self.id,
                cgsy_transaction_id=transaction.pk,
            )

    def _create_transaction(self, subscription):
        data = {
            'transaction_type': Transaction.BOLETO,
            'installments': self.installments,
            'installment_part': self.installment_part,
            'boleto_expiration_date': self.expiration_date,
            'boleto_url': self.link_boleto,
            'amount': self.amount,
            'card_hash': None,
            'lot_as_json': None,
        }

        form = PaymentForm(
            subscription=subscription,
            selected_lot=subscription.lot,
            data=data
        )
        form.is_valid()

        return form.save()

    def _sync_to_mix(self, db: MixConnection, mix_subscription):

        # Update boleto na MixEvents
        mix_insc_id = mix_subscription.mix_subscription_id

        try:

            db.connection.begin()

            register_id_caixa = False

            if self.paid is True and not self.idcaixa:
                sql = 'INSERT INTO caixa'
                sql += ' (inscricao, pagamento, valorpago, sitaucao, tipo)'
                sql += ' VALUES ({}, now(), {}, 02, 01)'
                sql = sql.format(self.id, self.amount)

                db.insert(sql)

                self.idcaixa = db.connection.insert_id()
                register_id_caixa = True

            sql = "UPDATE boleto SET link_boleto='{}'"

            if register_id_caixa is True:
                sql += ", idcaixa={}".format(self.idcaixa)

            sql += " WHERE idboleto={} AND idinscricao={}"
            sql = sql.format(self.id, mix_insc_id)

            db.update(sql)

        except DatabaseError:
            db.connection.rollback()
