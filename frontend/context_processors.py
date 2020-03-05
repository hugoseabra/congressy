"""
Sentry public DSN para suporte a erros do javascript
"""
import os

from django.conf import settings


def system_name(request):
    """
    Renderiza nome do sistema
    """
    return {
        'system_name': 'Visit SP'
    }


def system_owner_link(request):
    """
    Renderiza o link do dono do sistema.
    """
    return {
        'system_owner_link': 'https://visitsp.tur.br'
    }


def system_main_logo_path(request):
    """
    Renderiza o caminho de URL da logo principal
    """
    logo_path = os.path.join(
        settings.STATIC_DIR,
        'assets/img/header-logo_black.png'
    )

    return {
        'system_main_logo_path': logo_path,
    }


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
        'STAGING_MODE':
            '.settings.staging' in os.getenv('DJANGO_SETTINGS_MODULE'),
    }


def is_offline_server(request):
    return {'OFFLINE_SERVER': os.getenv('OFFLINE_SERVER') == 'True', }


def sentry_public_dsn(request):
    """
    Adicionar SENTRY_PUBLIC_DSN ao contexto de templates.
    """

    return {
        'SENTRY_PUBLIC_DSN': os.getenv('SENTRY_PUBLIC_DSN'),
    }
