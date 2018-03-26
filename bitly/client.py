"""
Cliente de acesso a funcionalidades do Bitly.
"""
from bitly.api import Connection
from django.conf import settings

from .exceptions import BitlyClientException


class BitlyClient(object):
    """ Cliente bitly, delegando as ações necessários para SDK do bitly. """

    def __init__(self) -> None:
        login = getattr(settings, 'BITLY_LOGIN')
        key = getattr(settings, 'BITLY_API_KEY')
        token = getattr(settings, 'BITLY_ACCESS_TOKEN')

        if not (login and key and token):
            raise BitlyClientException(
                "Bit.ly credentials not found in settings."
            )

        self.bitly = Connection(login=login, api_key=key, access_token=token)

    def shorten(self, link):
        """ Shortens url. """
        return self.bitly.shorten(uri=link)

    def clicks(self, link, **kwargs):
        """ Gets all clicks of hash an already shortened link. """
        return self.bitly.link_clicks(link=link, **kwargs)

    def referrers(self, link, **kwargs):
        """ Gets all referrers of hash an already shortened link. """
        return self.bitly.link_referrers_by_domain(link, **kwargs)
