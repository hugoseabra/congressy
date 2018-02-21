"""
Sentry public DSN para suporte a erros do javascript
"""
import os
import hmac


def sentry_public_dsn(request):
    """
    Adicionar SENTRY_PUBLIC_DSN ao contexto de templates.
    """
    return {
        'SENTRY_PUBLIC_DSN': os.getenv('SENTRY_PUBLIC_DSN'),
    }


def tawkto_secure_hash(request):
    """
    Adicionar hash de segurança do Tawkto utilizando a chave de api
    em TAWTO_API_KEY.
    """

    hmac.new("sharedpassword", "", hashlib.sha256).hexdigest()

    return {
        'TAWTO_SECURE_HASH': os.getenv('SENTRY_PUBLIC_DSN'),
    }
