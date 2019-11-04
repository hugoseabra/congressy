# pylint: skip-file
#############################################################################
# CUIDADO!!!
# A configuração de banco de dados é gerada automaticamente pelo deploy.
# Não mude as configurações de DATABASES.
#############################################################################
import re

from .common import *

# ========================== BASE CONFIGURATION ============================= #
DEBUG = False
# ================================= APPS ==================================== #
INSTALLED_APPS.extend([
    'raven.contrib.django.raven_compat',
])

if os.getenv('OFFLINE_SERVER') == 'True':
    INSTALLED_APPS.extend([
        'sync_client',
    ])

# ============================= MIDDLEWARES ================================= #
# SENTRY User Feedback
# We recommend putting this as high in the chain as possible
MIDDLEWARE_CLASSES.append(
    'raven.contrib.django.raven_compat.middleware.'
    'SentryResponseErrorIdMiddleware'
)
# Sentry logging
MIDDLEWARE_CLASSES.append(
    'raven.contrib.django.raven_compat.middleware.Sentry404CatchMiddleware',
)

IGNORABLE_404_URLS = (
    re.compile('/coupon/'),
)
# ============================= TEMPLATES =================================== #
# Sentry public DSN to template as SENTRY_PUBLIC_DSN
TEMPLATES[0]['OPTIONS']['context_processors'].append(
    'frontend.context_processors.sentry_public_dsn'
)

# ============================== LOGGING ==================================== #
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'root': {
        'level': 'WARNING',
        'handlers': ['sentry'],
    },
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s '
                      '%(process)d %(thread)d %(message)s'
        },
    },
    'handlers': {
        'sentry': {
            'level': 'ERROR',
            # To capture more than ERROR, change to WARNING, INFO, etc.
            'class': 'raven.contrib.django.raven_compat.handlers.SentryHandler',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        }
    },
    'loggers': {
        'django.db.backends': {
            'level': 'ERROR',
            'handlers': ['console'],
            'propagate': False,
        },
        'raven': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': False,
        },
        'sentry.errors': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': False,
        },
    },
}
# ============================ E-MAIL/SPARKPOST ============================= #
EMAIL_BACKEND = 'sparkpost.django.email_backend.SparkPostEmailBackend'
SPARKPOST_API_KEY = '6dacd78f4c49080da7bbe942d4f36dc95d0c110a'
# ================================ PAGAR.ME ================================= #
PAGARME_API_KEY = 'ak_live_7Rxgr3GlxWycVDMNeeG2InzwPsoPrM'
PAGARME_ENCRYPTION_KEY = 'ek_live_Hlpg45VTiyNOnAE4dmkEBbQDEtUZCX'
PAGARME_RECIPIENT_ID = 're_cjaskozwr01u1of5zo7kc962u'

# Usado para gerar card hash de cartões de crédito.
PAGARME_PUBLIC_KEY = '-----BEGIN PUBLIC KEY-----\n'
PAGARME_PUBLIC_KEY += \
    'MIIBIDANBgkqhkiG9w0BAQEFAAOCAQ0AMIIBCAKCAQEA00Nq1oNzuvcuRYppBo24\n'
PAGARME_PUBLIC_KEY += \
    'hGxV2zEtKA90CmtOm94rzHYFnbZnQyYPhwYeGDTdPKkjnayeiNrZTnYkq6dTKefd\n'
PAGARME_PUBLIC_KEY += \
    '67qXiz5T76BpZ6axMGtZfaS9Dn4RpBwy5OnfspElmMI5tYMNq96gSDbnj2hA1qZr\n'
PAGARME_PUBLIC_KEY += \
    'S0FET5+DTT23nn+HtVYJ23boU8fuIRJkJj4jlBBKLQQ9Z1Kw20wWiSN0XzktLzzx\n'
PAGARME_PUBLIC_KEY += \
    'KePqU3mXUCFE2oWJ15Ul+IibAcF2QWPKU8BBXMtrjG7Z7FkKrtWwsksgI6Iq/cgo\n'
PAGARME_PUBLIC_KEY += \
    'QkXoRc7hgSQgnoFkF30KOg6OQRG6lj7qg1p+KqFyAD9KlFKq1ICYnSngNsKSNIhm\n'
PAGARME_PUBLIC_KEY += '9wIBAw==\n'
PAGARME_PUBLIC_KEY += '-----END PUBLIC KEY-----\n'
# ============================== SENTRY ===================================== #
# Sentry integration
RAVEN_CONFIG = {
    'environment': 'production',
    'dsn': '{{ SENTRY_PRIVATE_DSN }}',
    'release': '{{ APP_VERSION }}',
}
