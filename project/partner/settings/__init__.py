# pylint: skip-file
from project.base_settings import *

# ========================== BASE CONFIGURATION ============================= #
ROOT_URLCONF = 'project.partner.urls'
# ================================= APPS ==================================== #
INSTALLED_APPS += [
    'gatheros_event',
    'gatheros_subscription',
    'gatheros_front',
    'mailer',
    'payment_debt',
    'payment',
    'partner',
    'hotsite',
    'survey',
    'addon',
    'associate',
    # 'bitly',
    'scientific_work',
    'certificate',
    'raffle',
    'importer',
    'attendance',
    'service_tags',
    'mix_boleto',
    'installment',
    'cgsy_commands',
]
# ========================= SERVER CONFIGURATION ============================ #
WSGI_APPLICATION = 'project.wsgi.application'

SITE_ID = os.getenv('SITE_ID', 2)

STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATIC_URL = '/static-manage/'

# @TODO Mudar para /media em produção.
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media-manage/'
# ============================== FIXTURES =================================== #
FIXTURE_DIRS += [
    os.path.join(BASE_DIR, 'project', 'partner', 'fixtures'),
]
