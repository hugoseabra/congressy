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


class TransactionStatusIntegratorError(Error):
    """Raised when an operation attempts to integrate a state update with a
        some other status.

    Attributes:
        message -- explanation of why the specific transaction is not allowed
    """

    def __init__(self, message):
        self.message = message
