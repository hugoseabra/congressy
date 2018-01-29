# pylint: skip-file

from . import *

DEBUG = True

INSTALLED_APPS.extend(['debug_toolbar', 'django_extensions'])

MIDDLEWARE_CLASSES.append('debug_toolbar.middleware.DebugToolbarMiddleware')


ABSOLUTEURI_PROTOCOL = 'http'


EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

MEDIA_ROOT = os.path.join(BASE_DIR, 'media_staging')

MIDDLEWARE_CLASSES.append('debug_toolbar.middleware.DebugToolbarMiddleware')


PAGARME_API_KEY = 'ak_test_IkLKxOIdD0GVTHfmlSPA1zuGoaCQtd'
PAGARME_RECIPIENT_ID = 're_cjcupb1iq0200zl6d89r92s32'

