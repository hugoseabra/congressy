# pylint: skip-file
#############################################################################
# CUIDADO!!!
# A configuração de banco de dados é gerada automaticamente pelo deploy.
# Não mude as configurações de DATABASES.
#############################################################################

# ================================= APPS ==================================== #
from project.frontend import get_frontend_loader
from . import *

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
GOOGLE_MAPS_API_KEY = 'GOOGLE_MAPS_API_KEY'

# ============================ WKHTMLTOPDF  ================================== #
WKHTMLTOPDF_WS_URL = 'http://wkhtmltopdf'

# =============================== CELERY ==================================== #
CELERY_BROKER_URL = 'amqp://{{ RABBITMQ_USER }}:{{ RABBITMQ_PASS }}@{{ RABBITMQ_SERVER }}:5672/'
CELERY_RESULT_BACKEND = 'amqp://{{ RABBITMQ_USER }}:{{ RABBITMQ_PASS }}@{{ RABBITMQ_SERVER }}:5672/'

# ======================== HEALTH CHECK - RABBITMQ ========================== #
BROKER_URL = CELERY_BROKER_URL

# ============================ FRONTEND ===================================== #
FRONTEND_DEBUG = os.getenv('FRONTEND_DEBUG', DEBUG)
frontend_loader = get_frontend_loader(
    front_end_dir_path=os.path.join(BASE_DIR, 'frontend', 'vue_frontend'),
    debug_mode=eval(str(FRONTEND_DEBUG)) is True,
)
WEBPACK_LOADER = dict(frontend_loader)

# ============================== VIDEOS ===================================== #
CGSY_VIDEOS_API_ADMIN_TOKEN = '4352cababfd0f7912869a5c7d2b90144e963dff1'
CGSY_VIDEOS_API_URL = 'https://api.congressy.com'
