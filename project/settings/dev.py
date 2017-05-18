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
