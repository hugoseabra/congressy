class Error(Exception):
    """Base class for exceptions in this module."""
    pass


class TransactionError(Error):
    """Raised when an operation attempts a  transaction that's not allowed.

    Attributes:
        message -- explanation of why the specific transaction is not allowed
    """

    def __init__(self, message):
        self.message = message
