# pylint: skip-file
from project.base_settings import *

# ========================== BASE CONFIGURATION ============================= #
ROOT_URLCONF = 'project.affiliate.urls'
# ================================= APPS ==================================== #
INSTALLED_APPS += [
    'gatheros_event',
    'gatheros_subscription',
    'payment',
    'mailer',
    'affiliate',
    'hotsite',
]
# ========================= SERVER CONFIGURATION ============================ #
WSGI_APPLICATION = 'project.wsgi.application'

SITE_ID = 2

STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATIC_URL = '/static/'

# @TODO Mudar para /media em produção.
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'
# ============================== FIXTURES =================================== #
FIXTURE_DIRS += [
    os.path.join(BASE_DIR, 'project', 'affiliate', 'fixtures'),
]
# ========================== AFFILIATE ====================================== #
# Valor maximo que afiliado a um evento pode participar da comissão por
# inscrição.
AFFILIATE_MAX_PERCENTAGE = 15.00
