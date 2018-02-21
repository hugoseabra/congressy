"""
Sentry public DSN para suporte a erros do javascript
"""
import os


def sentry_public_dsn():
    """
    Adicionar SENTRY_PUBLIC_DSN ao contexto de templates.
    """

    return {
        'SENTRY_PUBLIC_DSN': os.getenv('SENTRY_PUBLIC_DSN'),
    }
