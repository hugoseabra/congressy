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
])

ABSOLUTEURI_PROTOCOL = 'http'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# Host for sending e-mail.
EMAIL_HOST = '0.0.0.0'

# Port for sending e-mail.
EMAIL_PORT = 1025

# Optional SMTP authentication information for EMAIL_HOST.
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
EMAIL_USE_TLS = False


MEDIA_ROOT = os.path.join(BASE_DIR, 'media_dev')

MIDDLEWARE_CLASSES.append('debug_toolbar.middleware.DebugToolbarMiddleware')

INTERNAL_IPS = ['127.0.0.1']

PAGARME_API_KEY = 'ak_test_IkLKxOIdD0GVTHfmlSPA1zuGoaCQtd'

PAGARME_ENCRYPT_KEY = 'ek_test_ep7xk51I1XtWg58B9xij1VFwJRLcKa'

PAGARME_RECIPIENT_ID = 're_cjcupb1iq0200zl6d89r92s32'
