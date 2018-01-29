# pylint: skip-file

from . import *

DEBUG = True

INSTALLED_APPS.append('debug_toolbar')
INSTALLED_APPS.append('django_extensions')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'cgsy_dev',
        'USER': 'cgsy',
        'PASSWORD': 'GatherosAdmin@#qwe',
        'HOST': 'localhost',
    },
}

ABSOLUTEURI_PROTOCOL = 'http'

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

MEDIA_ROOT = os.path.join(BASE_DIR, 'media_dev')

MIDDLEWARE_CLASSES.append('debug_toolbar.middleware.DebugToolbarMiddleware')

INTERNAL_IPS = ['127.0.0.1']

PAGARME_API_KEY = 'ak_test_IkLKxOIdD0GVTHfmlSPA1zuGoaCQtd'

PAGARME_RECIPIENT_ID = 're_cjcupb1iq0200zl6d89r92s32'
