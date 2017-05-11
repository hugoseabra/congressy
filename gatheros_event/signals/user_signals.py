from django.contrib.auth.models import User
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver

from gatheros_event.acl import gatheros_user_context


@receiver(user_logged_in, sender=User)
def add_user_context(user, request, **_):
    # Se usuário está logado, força a existência do mesmo na requisição
    request.user = user
    gatheros_user_context.update_user_context(request)


@receiver(user_logged_out, sender=User)
def destroy_user_context(request, **_):
    gatheros_user_context.clean_user_context(request)
