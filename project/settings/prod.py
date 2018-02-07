# pylint: skip-file
#############################################################################
# CUIDADO!!!
# A configuração de banco de dados é gerada automaticamente pelo deploy.
# Não mude as configurações de DATABASES.
#############################################################################

from . import *

# ========================== BASE CONFIGURATION ============================= #
DEBUG = False
# ================================= APPS ==================================== #
INSTALLED_APPS.extend([
    'raven.contrib.django.raven_compat',
])
# ================================ CELERY =================================== #
CELERY_BROKER_URL = 'redis://redis:6379/0'
CELERY_RESULT_BACKEND = 'redis://redis:6379/0'
# ============================ E-MAIL/SPARKPOST ============================= #
SPARKPOST_API_KEY = '6dacd78f4c49080da7bbe942d4f36dc95d0c110a'
EMAIL_BACKEND = 'sparkpost.django.email_backend.SparkPostEmailBackend'
