"""
Sentry public DSN para suporte a erros do javascript
"""
import os

from django.conf import settings


def render_app_only(request):
    """
    Verificar se querystring 'apponly' e 'notitle'
    são passadas na url e, se sim, inserir no contexto.
    """
    apponly = request.GET.get('apponly')
    notitle = request.GET.get('notitle')

    return {
        'apponly': apponly == '1',
        'notitle': notitle == '1',
    }


def is_debug_mode(request):
    return {
        'debug': settings.DEBUG is True,
        'DEBUG': settings.DEBUG is True,
    }


def sentry_public_dsn(request):
    """
    Adicionar SENTRY_PUBLIC_DSN ao contexto de templates.
    """

    return {
        'SENTRY_PUBLIC_DSN': os.getenv('SENTRY_PUBLIC_DSN'),
    }
