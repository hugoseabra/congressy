# pylint: skip-file
#############################################################################
# CUIDADO!!!
# A configuração de banco de dados é gerada automaticamente pelo deploy.
# Não mude as configurações de DATABASES.
#############################################################################

from . import *
import raven

# ========================== BASE CONFIGURATION ============================= #
DEBUG = False
SECRET_KEY = '{{ SECRET_KEY }}'

# ========================= SERVER CONFIGURATION ============================ #
ABSOLUTEURI_PROTOCOL = 'https'
# ================================= APPS ==================================== #
INSTALLED_APPS.extend([
    'raven.contrib.django.raven_compat',
])
# ========================= SERVER CONFIGURATION ============================ #
SITE_ID = 2
# ============================== DATABASE =================================== #
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': '{{ DBNAME }}',
        'USER': '{{ DBUSER }}',
        'PASSWORD': '{{ DBPASS }}',
        'PORT': '{{ DBPORT }}',
        'HOST': '{{ DBHOST }}',
    },
}
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
# ============================= TEMPLATES =================================== #
# Sentry public DSN to template as SENTRY_PUBLIC_DSN
TEMPLATES[0]['OPTIONS']['context_processors'].append(
    'frontend.context_processors.sentry_public_dsn'
)
# ================================ CELERY =================================== #
CELERY_BROKER_URL = 'redis://redis:6379/0'
CELERY_RESULT_BACKEND = 'redis://redis:6379/0'
# ============================ E-MAIL/SPARKPOST ============================= #
EMAIL_BACKEND = 'sparkpost.django.email_backend.SparkPostEmailBackend'
SPARKPOST_API_KEY = '6dacd78f4c49080da7bbe942d4f36dc95d0c110a'
# ============================== SENTRY ===================================== #
# Sentry integration
RAVEN_CONFIG = {
    'environment': 'production',
    'dsn': '{{ SENTRY_PRIVATE_DSN }}',
    'release': '{{ APP_VERSION }}',
}
# ================================ PAGAR.ME ================================= #
PAGARME_API_KEY = 'ak_live_7Rxgr3GlxWycVDMNeeG2InzwPsoPrM'
PAGARME_ENCRYPTION_KEY = 'ek_live_Hlpg45VTiyNOnAE4dmkEBbQDEtUZCX'
PAGARME_RECIPIENT_ID = 're_cjaskozwr01u1of5zo7kc962u'
