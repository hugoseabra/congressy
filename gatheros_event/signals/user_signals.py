""" Signals do model `User` """
from django.contrib.auth.models import User
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver

from gatheros_event.helpers import account
from gatheros_event.models import Person


@receiver(user_logged_in, sender=User)
def update_account(request, user, **_):
    """ Atualiza informações de conta na sessão do usuário. """
    # Adiciona o usuário na requisição pois os helpers de account precisam
    request.user = user

    try:
        user.person is not None
    except Person.DoesNotExist:
        return

    account.update_account(request)


@receiver(user_logged_out)
def clean_account(request, **_):
    """ Limpa dados de conta na sessão do usuário. """
    account.clean_account(request)
