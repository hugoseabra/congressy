from mix_boleto.mix.boleto import MixBoleto
from mix_boleto.mix.category import MixCategory
from mix_boleto.mix.connection import MixConnection
from mix_boleto.mix.lot import MixLot
from mix_boleto.mix.subscription import MixSubscription
from payment.helpers.payment_helpers import decimal_processable_amount


class MixSubscriptionCollectionBuilder(object):
    """

    Classe responsável para conectar-se ao banco de dados da MixEvents e
    construir objetos necessários a partir do resgate dos dados do banco de
    dados para poder criar uma coleção de MixSubscription's

        - MixCategory;
        - MixLot;
        - MixSubscription;
        - MixBoleto;
    """

    def __init__(self, db: MixConnection, event_id: int,) -> None:
        """
        Construtor

        :param db: Uma conexão com o banco de dados
        :param event_id: chave primaria de evento
        """
        self.event_pk = event_id
        self.connection = db

    def build(self, mix_subscription_id=None) -> list:
        """
            Responsavel por montar uma coleção de MixSubscription's

        :return: lista de MixSubscriptions
        """

        mix_subscriptions = list()

        boletos = self._build_boletos_collection()

        for subscription in self._fetch_subscriptions(mix_subscription_id):
            mix_subscription = self._build_subscription(subscription)
            if subscription['idinscricao'] in boletos:
                for boleto in boletos[subscription['idinscricao']]:
                    mix_subscription.add_boleto(boleto)
            mix_subscriptions.append(mix_subscription)

        return mix_subscriptions

    def _fetch_subscriptions(self, mix_subscription_id):
        sql = "SELECT * FROM inscricao"
        sql += " INNER JOIN preco USING (idcategoria)"
        sql += " INNER JOIN categoria USING (idcategoria)"
        sql += " WHERE idinscricao IN ("
        sql += "    SELECT DISTINCT idinscricao FROM boleto WHERE situacao = 1"
        sql += " )"

        if mix_subscription_id:
            sub_sql = " AND idinscricao={}".format(
                int(mix_subscription_id)
            )
            sql += sub_sql

        sql += " GROUP BY idinscricao"

        return self.connection.fetch(sql)

    def _build_subscription(self, subscription_data: dict) -> MixSubscription:
        """
            Responsavel por criar uma instancia de MixSubscription


        :param subscription_data: dict de dados
        :return: instancia de MixSubscription
        """
        mix_subscription_id = subscription_data['idinscricao']
        category = self._build_category(subscription_data)
        lot = self._build_lot(subscription_data, category)
        created = subscription_data['_crdt']
        updated = subscription_data['_updt']

        sub = MixSubscription(
            mix_subscription_id=mix_subscription_id,
            mix_category=category,
            mix_lot=lot,
            created=created,
            updated=updated,
        )

        sub.set_person_data(
            name=subscription_data['nome'],
            gender=subscription_data['sexo'],
            email=subscription_data['email'],
            cpf=subscription_data['cpf'],
            phone=subscription_data['fones'],
            street=subscription_data['endereco'],
            complement=subscription_data['complemento'],
            number=subscription_data['numero'],
            village=subscription_data['bairro'],
            zip_code=subscription_data['cep'],
            city=subscription_data['cidade'],
            uf=subscription_data['uf'],
            institution=subscription_data['instituicao'],
            cnpj=subscription_data['cnpj'],
        )

        return sub

    def _build_category(self, subscription_data: dict) -> MixCategory:
        """
            Responsavel por criar uma categoria

        :param subscription_data: dict de dados
        :return: instance de MixCategory
        """
        category_id = subscription_data['idcategoria']
        category_name = subscription_data['categoria.nome']
        category_created = subscription_data['categoria._crdt']
        category_update = subscription_data['categoria._updt']

        return MixCategory(
            event_id=self.event_pk,
            id=category_id,
            name=category_name,
            created=category_created,
            updated=category_update,
        )

    # noinspection PyMethodMayBeStatic
    def _build_lot(self,
                   subscription_data: dict,
                   category: MixCategory) -> MixLot:
        """
            Responsavel pela criação de lote

        :param subscription_data: dict de dados
        :param category: instancia de MixCategory
        :return: instancia de MixLot
        """
        lot_price = subscription_data['valor']
        lot_date_limit = subscription_data['limite']

        return MixLot(
            mix_category=category,
            price=lot_price,
            date_limit=lot_date_limit
        )

    # noinspection PyMethodMayBeStatic
    def _build_boleto(self, boleto_data: dict) -> MixBoleto:
        """
            Responsavel pela criação de uma instancia de MixBoleto

        :param boleto_data:
        :return: instancia de MixBoleto
        """

        return MixBoleto(
            id=boleto_data['idboleto'],
            id_caixa=boleto_data['idcaixa'],
            expiration_date=boleto_data['vencimento'],
            amount=decimal_processable_amount(boleto_data['valor']),
            installments=boleto_data['parcn'],
            installment_part=boleto_data['parci'],
            link_boleto=boleto_data['link_boleto'],
            created=boleto_data['_crdt'],
            updated=boleto_data['_updt'],
            cancelled=False,
        )

    def _build_boletos_collection(self) -> dict:
        """

            Responsavel pela criação de um dict com idinscricao como chave e
            uma lista de boletos como valores

        :return: dict de boletos com idinscricao como chave e lista de
        boletos como valor
        """

        boletos = dict()

        boletos_data = self.connection.fetch(
            'SELECT * FROM boleto WHERE situacao = 1 ORDER BY parci'
        )

        for payload in boletos_data:

            if payload['idinscricao'] not in boletos.keys():
                boletos[payload['idinscricao']] = list()

            boletos[payload['idinscricao']].append(
                self._build_boleto(payload)
            )

        return boletos
