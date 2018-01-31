# pylint: skip-file

from . import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'cgsyplatform',
        'USER': 'congressy',
        'PASSWORD': 'congressy',
        'HOST': 'localhost',
    },
}

DEBUG = True

INSTALLED_APPS.extend([
    'debug_toolbar',
    'django_extensions',

])

ABSOLUTEURI_PROTOCOL = 'http'

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

MEDIA_ROOT = os.path.join(BASE_DIR, 'media_dev')

MIDDLEWARE_CLASSES.append('debug_toolbar.middleware.DebugToolbarMiddleware')

INTERNAL_IPS = ['127.0.0.1']

PAGARME_API_KEY = 'ak_test_IkLKxOIdD0GVTHfmlSPA1zuGoaCQtd'

PAGARME_RECIPIENT_ID = 're_cjcupb1iq0200zl6d89r92s32'
