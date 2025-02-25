class BittleException(Exception):
    """
    This is a custom exception which gets raised if there are any troubles
    with the Bittle django model or bit.ly access itself.
    """
    pass


class BitlyClientException(Exception):
    """
    This is a custom exception which gets raised if there are any troubles
    with the Bitly Client happens.
    """
    pass
