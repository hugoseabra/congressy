# pylint: skip-file
from project.base_settings import *

# ========================== BASE CONFIGURATION ============================= #
ROOT_URLCONF = 'project.manage.urls'
# ================================= APPS ==================================== #
INSTALLED_APPS += [
    'gatheros_event',
    'gatheros_subscription',
    'gatheros_front',
    'mailer',
    'payment',
    'hotsite',
    'bitly',
]
# =========================== AUTH BACKENDS ================================= #
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/manage/'
LOGOUT_REDIRECT_URL = '/login/'
# ========================= SERVER CONFIGURATION ============================ #
WSGI_APPLICATION = 'project.wsgi.application'

SITE_ID = 1

STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATIC_URL = '/static/'

# @TODO Mudar para /media em produção.
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'
# ============================== FIXTURES =================================== #
FIXTURE_DIRS += [
    os.path.join(BASE_DIR, 'project', 'manage', 'fixtures'),
    os.path.join(BASE_DIR, 'gatheros_event', 'tests', 'fixtures'),
    os.path.join(BASE_DIR, 'gatheros_subscription', 'tests', 'fixtures'),
    os.path.join(BASE_DIR, 'payment', 'tests', 'fixtures'),
]
# ============================= TEMPLATES =================================== #
TEMPLATES[0]['OPTIONS']['context_processors'].append(
    'gatheros_event.context_processors.account',
)
# ============================= PAYMENT ===================================== #
# Planos da congressy, contemplam percentuais de recebimento em cima das
# transações

# Valor mínimo que a congrssy deve receber por transação. Se o valor do recebi
# devido for menor do que este, o valor da transaçaõ da parte da congressy será
# este valor.
CONGRESSY_MINIMUM_AMOUNT = 4.99
