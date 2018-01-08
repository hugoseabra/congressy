# pylint: skip-file
import os

from django.contrib.messages import constants as message_constants

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))

SECRET_KEY = '1@==vhll7d5v(%=t++oy-38+639o-4*f73^!o=v!a^z$#(6x%$'

DEBUG = False

ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    # DJANGO_APPS
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.postgres',
    'django.contrib.humanize',
    'django.contrib.sites',

    # THIRD PARTY
    'celery',
    'mailer',
    'permission',
    'stdimage',
    'ckeditor',
    'datetimewidget',
    'widget_tweaks',
    'rest_framework',
    'rest_framework.authtoken',

    # KANU_APPS
    'kanu_locations',
    'kanu_form',

    # GATHEROS_APPS
    'core',
    'frontend',
    'gatheros_event',
    'gatheros_subscription',
    'gatheros_front',
    'hotsite',
]

SITE_ID = 1

MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'project.urls'

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',  # default
    'permission.backends.PermissionBackend',  # django-permission
]


class InvalidTemplateVariable(str):
    def __mod__(self, other):
        from django.template.base import TemplateSyntaxError
        raise TemplateSyntaxError("Invalid variable : '%s'" % other)


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'gatheros_event/templates/'),
            os.path.join(BASE_DIR, 'frontend/templates/'),
            os.path.join(BASE_DIR, 'hotsite/templates'),
            os.path.join(BASE_DIR, 'mailer/templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'string_if_invalid': InvalidTemplateVariable("%s"),
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'gatheros_event.context_processors.account',
            ],
            'builtins': [
                'permission.templatetags.permissionif',
            ],
        },
    },
]

WSGI_APPLICATION = 'project.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'gatheros_site',
        'USER': 'MUDAR_USUARIO',
        'PASSWORD': 'MUDAR_SENHA',
        'HOST': 'localhost',
        'PORT': '',
    },
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.'
                'UserAttributeSimilarityValidator',
    },
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    )
}

LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_L10N = True
USE_TZ = False

STATIC_URL = '/static/'
# noinspection PyUnresolvedReferences
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)


MEDIA_ROOT = os.path.join(BASE_DIR, 'media_dev')
MEDIA_URL = '/media/'

FIXTURE_DIRS = [
    os.path.join(BASE_DIR, 'fixtures'),
    os.path.join(BASE_DIR, 'gatheros_event/tests/fixtures'),
    os.path.join(BASE_DIR, 'gatheros_subscription/tests/fixtures'),
]

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/login/'

GOOGLE_MAPS_API_KEY = 'AIzaSyD6ejnl_NChhfZhI_GoNT12FfCVCdOlgtw'

CKEDITOR_CONFIGS = {
    'default': {
        'width': '100%',
        'height': 150,
    },
}

MESSAGE_TAGS = {
    message_constants.DEBUG: 'debug',
    message_constants.INFO: 'info',
    message_constants.SUCCESS: 'success',
    message_constants.WARNING: 'warning',
    message_constants.ERROR: 'danger',
}