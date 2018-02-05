# pylint: skip-file
import os

from django.utils.translation import ugettext_lazy as _



from django.contrib.messages import constants as message_constants

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))

SECRET_KEY = '1@==vhll7d5v(%=t++oy-38+639o-4*f73^!o=v!a^z$#(6x%$'

DEBUG = False

ALLOWED_HOSTS = ['*']

X_FRAME_OPTIONS = 'ALLOWALL'
XS_SHARING_ALLOWED_METHODS = ['POST', 'GET', 'OPTIONS', 'PUT', 'DELETE']

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

    # Django added apps
    'django.contrib.sites',
    'django.forms',

    # THIRD PARTY
    'absoluteuri',
    'permission',
    'stdimage',
    'ckeditor',
    'datetimewidget',
    'widget_tweaks',
    'django_user_agents',
    'rest_framework',
    'rest_framework.authtoken',

    # KANU_APPS
    'kanu_locations',

    # GATHEROS_APPS
    'frontend',
    'gatheros_event',
    'gatheros_subscription',
    'gatheros_front',
    'mailer',
    'payment',
    'core',
    'hotsite',
]

# Added to allow overriding django forms templates.
FORM_RENDERER = 'django.forms.renderers.TemplatesSetting'

SITE_ID = 1

MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_user_agents.middleware.UserAgentMiddleware',
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
            os.path.join(BASE_DIR, 'frontend', 'templates'),
            os.path.join(BASE_DIR, 'gatheros_event', 'templates'),
            os.path.join(BASE_DIR, 'hotsite', 'templates'),
            os.path.join(BASE_DIR, 'mailer', 'templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'string_if_invalid': InvalidTemplateVariable("%s"),
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.i18n',
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

# Name of cache backend to cache user agents. If it not specified default
# cache alias will be used. Set to `None` to disable caching.
# Uncomment this when cache is configured
# USER_AGENTS_CACHE = 'default'

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

STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATIC_URL = '/static/'

MEDIA_ROOT = os.path.join(BASE_DIR, 'media_dev')
MEDIA_URL = '/media/'

FIXTURE_DIRS = [
    os.path.join(BASE_DIR, 'fixtures'),
    os.path.join(BASE_DIR, 'gatheros_event/tests/fixtures'),
    os.path.join(BASE_DIR, 'gatheros_subscription/tests/fixtures'),
]

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/manage/'
LOGOUT_REDIRECT_URL = '/login/'

GOOGLE_MAPS_API_KEY = 'AIzaSyD6ejnl_NChhfZhI_GoNT12FfCVCdOlgtw'

CKEDITOR_CONFIGS = {
    'default': {
        'toolbar_Full': [
            '/',
            {
                'name': 'styles',
                'items': [
                    'Styles',
                    'Format',
                    'FontSize'
                ]
            },
            {
                'name': 'basicstyles',
                'items': [
                    'Bold',
                    'Italic',
                    'Underline',
                    'Strike',
                    '-',
                    'RemoveFormat'
                ]
            },
            {
                'name': 'paragraph',
                'items': [
                    'NumberedList',
                    'BulletedList',
                    '-',
                    'Outdent',
                    'Indent',
                    '-',
                    'JustifyLeft',
                    'JustifyCenter',
                    'JustifyRight',
                    'JustifyBlock'
                ]
            },
            {
                'name': 'links',
                'items': [
                    'Link',
                    'Unlink',
                    'Anchor'
                ]
            },
            {
                'name': 'insert',
                'items': [
                    'Table',
                    'HorizontalRule'
                ]
            },
            {
                'name': 'youcustomtools',
                'items': [
                    'Preview',
                    'Maximize',
                    'Source',
                ]
            },
        ],
        'toolbar': 'Full',
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

DEFAULT_FROM_EMAIL = 'Congressy <mail@congressy.net>'
CONGRESSY_REPLY_TO = 'Congressy <congressy@congressy.com>'
ALERT_EMAILS = ['nathan@congressy.com', 'hugo@congressy.com']
# Tell Django where the project's translation files should be.
LOCALE_PATHS = (
    os.path.join(BASE_DIR, 'locale'),
)


LANGUAGES = (
    ('en', _('English')),
    ('pt-br', _('Português')),
)

