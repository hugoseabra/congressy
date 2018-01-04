# pylint: skip-file

from .settings import *

DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'gatheros_site_dev',
        'USER': 'gatheros',
        'PASSWORD': 'GatherosAdmin@#qwe',
        'HOST': 'localhost',
    },
}

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

MEDIA_ROOT = os.path.join(BASE_DIR, 'media_dev')

MIDDLEWARE_CLASSES.append('debug_toolbar.middleware.DebugToolbarMiddleware')

INTERNAL_IPS = ['127.0.0.1']

INSTALLED_APPS.append('debug_toolbar')