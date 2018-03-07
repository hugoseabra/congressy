class Error(Exception):
    """Base class for exceptions in this module."""
    pass


class NotifcationError(Error):
    """Raised when an operation attempts a notification that's not allowed or
    misconfigured.

    Attributes:
        message -- explanation of why the specific transaction is not allowed
    """

    def __init__(self, message):
        self.message = message
