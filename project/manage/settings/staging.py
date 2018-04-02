# pylint: skip-file
#############################################################################
# CUIDADO!!!
# A configuração de banco de dados é gerada automaticamente pelo deploy.
# Não mude as configurações de DATABASES.
#############################################################################

from .common import *
from fnmatch import fnmatch

# ========================== BASE CONFIGURATION ============================= #
DEBUG = True
# ================================= APPS ==================================== #
INSTALLED_APPS.extend([
    'debug_toolbar',
    'django_nose',
    'logtailer',
])
# ============================= MIDDLEWARES ================================= #
# Django debug toolbar
MIDDLEWARE_CLASSES.append('debug_toolbar.middleware.DebugToolbarMiddleware')
# ========================= SERVER CONFIGURATION ============================ #
# MEDIA_ROOT = os.path.join(BASE_DIR, 'media_staging')
# ================================= E-MAIL ================================== #
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# Host for sending e-mail.
EMAIL_HOST = 'mailhog'
# Port for sending e-mail.
EMAIL_PORT = 1025
# Optional SMTP authentication information for EMAIL_HOST.
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
EMAIL_USE_TLS = False
# ================================ PAGAR.ME ================================= #
PAGARME_API_KEY = 'ak_test_IkLKxOIdD0GVTHfmlSPA1zuGoaCQtd'
PAGARME_ENCRYPTION_KEY = 'ek_test_ep7xk51I1XtWg58B9xij1VFwJRLcKa'
PAGARME_RECIPIENT_ID = 're_cjcupb1iq0200zl6d89r92s32'
PAGARME_TEST_RECIPIENT_ID = 're_cjdagxm5q00fqok6eeuukmmtp'
# ================================= NOSE ==========++======================== #
# Rodar com CODE COVERAGE para gerar HTML na pasta /cover.
# Use nose to run all tests
TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'

# Tell nose to measure coverage on the 'foo' and 'bar' apps
apps = 'gatheros_event,gatheros_front, gatheros_subscription,mailer'
NOSE_ARGS = [
    '--with-coverage',
    '--cover-package=' + apps,
]


# ============================ DEBUG TOOL BAR =============================== #
# Allows the use of regex IP's
class GlobList(list):
    def __contains__(self, key):
        for elt in self:
            if fnmatch(key, elt):
                return True
        return False


# Internal IP's used by DDTB
INTERNAL_IPS = GlobList(['*.*.*.*'])
