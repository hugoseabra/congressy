# pylint: skip-file

from . import *
import raven

INSTALLED_APPS.append('celery')
INSTALLED_APPS.append('raven.contrib.django.raven_compat')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'cgsy',
        'USER': 'cgsy',
        'PASSWORD': 'CgsyAdmin!@#qwe',
        'PORT': 5432,
        'HOST': 'postgres',  # Docker host
    },
}

ABSOLUTEURI_PROTOCOL = 'https'

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

CELERY_BROKER_URL = 'redis://redis:6379/0'
CELERY_RESULT_BACKEND = 'redis://redis:6379/0'

SPARKPOST_API_KEY = '6dacd78f4c49080da7bbe942d4f36dc95d0c110a'
EMAIL_BACKEND = 'sparkpost.django.email_backend.SparkPostEmailBackend'


PAGARME_API_KEY = 'ak_live_7Rxgr3GlxWycVDMNeeG2InzwPsoPrM'
PAGARME_RECIPIENT_ID = 're_cjaskozwr01u1of5zo7kc962u'

SENTRY_DSN = ''

RAVEN_CONFIG = {
    'dsn': SENTRY_DSN,
    # If you are using git, you can also automatically configure the
    # release based on the git info.
    'release': raven.fetch_git_sha(BASE_DIR),
}
