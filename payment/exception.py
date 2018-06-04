class Error(Exception):
    """Base class for exceptions in this module."""
    pass


# Receivers exception
class ReceiverAlreadyPublishedError(Error):
    """
    Erro: quando um objeto Receiver, com o mesmo recipient_id, é publicado e já
    existe um outro em seu lugar.

    Isso evitará que haja erros no processamento de recebedores.
    """

    def __init__(self, message):
        self.message = message


class ReceiverTotalAmountExceeded(Error):
    """
    Erro: quando o montante total dos recebedores ultrapassada o montante
    a ser transacionado.

    Isso evitará que haja erros na transação gerando splti maior que o valor
    a ser transacionado.
    """

    def __init__(self, message):
        self.message = message


class TransactionDataError(Error):
    """
    Quando a construção dados de transação não são feitas corretamente.

    Isso evitará tentativas de criação de transações de pagamento e possíveis
    transações incorretas.
    """

    def __init__(self, message):
        self.message = message


class TransactionMisconfiguredError(Error):
    """
    Quando há um processo de tentativa de transação, mas, por algum motivo,
    o evento não está configurado corretamente.

    Isso estabelecerá uma comunicação mais clara com o participante e
    poderá orientar a plataforma a orientar melhor o organizador.
    """

    def __init__(self, message):
        self.message = message


class TransactionError(Error):
    """ Raised when an operation attempts a  transaction that's not allowed.

    Attributes:
        message -- explanation of why the specific transaction is not allowed
    """

    def __init__(self, message):
        self.message = message


class RecipientError(Error):
    """
    Raised when an operation attempts something with a recipient and
    something goes wrong.

    Attributes:
        message -- explanation of why the specific transaction is not allowed
    """

    def __init__(self, message):
        self.message = message


class OrganizerRecipientError(Error):
    """
    Raised when an operation attempts something the Organizer recipient and
    something goes wrong.

    Attributes:
        message -- explanation of why the specific transaction is not allowed
    """

    def __init__(self, message):
        self.message = message


class StateNotAllowedError(Error):
    """Raised when an operation attempts a state update and breaks the rules.

    Attributes:
        message -- explanation of why the specific transaction is not allowed
    """

    def __init__(self, message):
        self.message = message


class TransactionApiError(Error):
    def __init__(self, message):
        self.message = message

class TransactionStatusError(Error):
    """Raised when an operation when a Status update could not be processed.

    Attributes:
        message -- explanation of why the specific transaction is not allowed
    """

    def __init__(self, message):
        self.message = message


class TransactionStatusIntegratorError(Error):
    """Raised when an operation attempts to integrate a state update with a
        some other status.

    Attributes:
        message -- explanation of why the specific transaction is not allowed
    """

    def __init__(self, message):
        self.message = message


class TransactionNotFound(Exception):
    """Raised when a transaction does not exist for a subscription.

    Attributes:
        message -- explanation of why the specific transaction is not allowed
    """

    def __init__(self):
        self.message = 'Transação não encontrada.'
