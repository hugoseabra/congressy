# pylint: skip-file
#############################################################################
# CUIDADO!!!
# A configuração de banco de dados é gerada automaticamente pelo deploy.
# Não mude as configurações de DATABASES.
#############################################################################

from . import *

# ================================= APPS ==================================== #
INSTALLED_APPS.extend([
    'django_uwsgi',
])
# ========================== BASE CONFIGURATION ============================= #
SECRET_KEY = '{{ SECRET_KEY }}'
# ========================= SERVER CONFIGURATION ============================ #
ABSOLUTEURI_PROTOCOL = 'https'
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
# =============================== CACHE ===================================== #
CACHES = {
    'default': {
        'BACKEND': 'uwsgicache.UWSGICache',
    }
}
# ============================ VALIDATORS =================================== #
AUTH_PASSWORD_VALIDATORS += [
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 6,
        }
    },
    # {
    #     'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    # },
    # @TODO inserir auditoria.
    # @TODO captcha tirar da sessão e colocar pesistência de tentivas em outro lugar.
    # {
    #     'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    # },
]
# ============================== GOOGLE ===================================== #
GOOGLE_MAPS_API_KEY = 'AIzaSyDCx_62viOjiSf-NFZ1m-1mQF-9-ize9EA'
