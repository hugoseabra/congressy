"""
Sentry public DSN para suporte a erros do javascript
"""
import os

from django.conf import settings

from project import system


def system_name(request):
    """
    Renderiza nome do sistema
    """
    return {
        'system_name': system.get_system_name()
    }


def system_owner_link(request):
    """
    Renderiza o link do dono do sistema.
    """
    return {
        'system_owner_link': system.get_system_owner_link()
    }


def system_owner_terms_link(request):
    """
    Renderiza o link do dono do sistema.
    """
    return {
        'system_owner_terms_link': system.get_system_owner_terms_link()
    }


def system_main_logo_path(request):
    """
    Renderiza o caminho de URL da logo principal
    """
    return {
        'system_main_logo_path': system.get_system_main_logo(),
    }


def system_voucher_logo_path(request):
    """
    Renderiza o caminho de URL da logo principal
    """
    return {
        'system_voucher_logo_path': system.get_system_voucher_logo(),
    }


def system_registration_logo_path(request):
    """
    Renderiza o caminho de URL da logo principal
    """
    return {
        'system_registration_logo_path': system.get_system_registration_logo(),
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
