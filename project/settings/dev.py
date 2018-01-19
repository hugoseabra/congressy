# pylint: skip-file

from . import *

DEBUG = True

INSTALLED_APPS.append('debug_toolbar')

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
