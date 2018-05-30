class Error(Exception):
    """Base class for exceptions in this module."""
    pass

# Receivers exceptions
class ReceiverAlreadyPublishedError(Error):
    """
    Erro: quando um objeto Receiver, com o mesmo recipient_id, é publicado e já
    existe um outro em seu lugar.

    Isso evitará que haja erros no processamento de recebedores.
    """
    def __init__(self, message):
        self.message = message
