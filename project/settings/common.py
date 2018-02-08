# pylint: skip-file
#############################################################################
# CUIDADO!!!
# A configuração de banco de dados é gerada automaticamente pelo deploy.
# Não mude as configurações de DATABASES.
#############################################################################

from project.settings import *

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
# ============================ VALIDATORS =================================== #
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
# ============================= PAGAR.ME ==================================== #
PAGARME_API_KEY = 'ak_live_7Rxgr3GlxWycVDMNeeG2InzwPsoPrM'
PAGARME_ENCRYPTION_KEY = 'ek_live_Hlpg45VTiyNOnAE4dmkEBbQDEtUZCX'
PAGARME_RECIPIENT_ID = 're_cjaskozwr01u1of5zo7kc962u'
