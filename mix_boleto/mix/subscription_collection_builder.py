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

    def __init__(self, db: MixConnection, event_id: int) -> None:
        """
            Construtor
            
        :param db: Uma conexão com o banco de dados
        :param event_id: chave primaria de evento
        """
        self.event_pk = event_id
        self.connection = db
        self.query = self.connection.fetch(
            'SELECT * FROM inscricao '
            'INNER JOIN preco USING (idcategoria)'
            'INNER JOIN categoria USING (idcategoria)'
            'WHERE idinscricao IN (SELECT DISTINCT idinscricao FROM boleto '
            'WHERE situacao = 1) GROUP BY idinscricao'
        )

    def build(self) -> list:
        """
            Responsavel por montar tudo

        :return: lista de MixSubscriptions
        """

        mix_subscriptions = list()

        boletos = self._build_boletos_collection()

        for subscription in self.query:
            mix_subscription = self._build_subscription(subscription)
            if subscription['idisncricao'] in boletos:
                for boleto in boletos[subscription['idisncricao']]:
                    mix_subscription.add_boleto(boleto)
            mix_subscriptions.append(mix_subscription)

        return mix_subscriptions

    def _build_subscription(self, subscription_data: dict):
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

    def _build_category(self, subscription_data: dict):
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
    def _build_lot(self, subscription_data: dict, category: MixCategory):
        """
            Responsavel pela criação de lotes

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
    def _build_boleto(self, boleto_data: dict):

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

    def _build_boletos_collection(self):

        boletos = dict()

        boletos_data = self.connection.fetch(
            'SELECT * FROM boleto WHERE situacao = 1'
        )

        for payload in boletos_data:
            if boletos_data['idinscricao'] not in boletos:
                boletos[boletos_data['idinscricao']] = list()

            boletos[boletos_data['idinscricao']].append(
                self._build_boleto(payload)
            )

        return boletos
