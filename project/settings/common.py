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
GOOGLE_MAPS_API_KEY = 'AIzaSyAPpiE3QALhF_5AhBSZJ9K27eDiJXCtTK0'
# ============================= PAGAR.ME ==================================== #
PAGARME_API_KEY = 'ak_live_7Rxgr3GlxWycVDMNeeG2InzwPsoPrM'
PAGARME_ENCRYPTION_KEY = 'ek_live_Hlpg45VTiyNOnAE4dmkEBbQDEtUZCX'
PAGARME_RECIPIENT_ID = 're_cjaskozwr01u1of5zo7kc962u'
