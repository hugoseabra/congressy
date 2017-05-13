from django.contrib.auth.models import User
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver

from gatheros_event.helpers import account


@receiver(user_logged_in, sender=User)
def update_session_account(request, user, **_):
    # Adiciona o usuário na requisição pois os helpers de account precisam
    request.user = user
    account.update_session_account(request)


@receiver(user_logged_out)
def clean_session_account(request, **_):
    account.clean_session_account(request)
