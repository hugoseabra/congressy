from .settings import *

DEBUG = True

# INSTALLED_APPS += [
#     'behave_django',
# ]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'gatheros_site_teste',
        'USER': 'gatheros',
        'PASSWORD': 'GatherosAdmin@#qwe',
        'HOST': 'localhost',
    },
}
