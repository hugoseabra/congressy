# pylint: skip-file
import os

from django.contrib.messages import constants as message_constants
from django.utils.translation import ugettext_lazy as _

# ========================== BASE CONFIGURATION ============================= #
BASE_DIR = os.path.abspath(os.path.join(
    os.path.dirname(__file__),
    '..',
))
DEBUG = False
# ================================= APPS ==================================== #
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
    'captcha',
    'wkhtmltopdf',

    # KANU_APPS
    'kanu_locations',

    # CONGRESSY APPS
    'core',
    'base',
    'frontend',
]
# ================= LOCATION/LANGUAGES/INTERNATIONALIZATION ================= #
LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_L10N = True
USE_TZ = False

# Tell Django where the project's translation files should be.
LOCALE_PATHS = (
    os.path.join(BASE_DIR, 'locale'),
)

LANGUAGES = (
    ('en', _('English')),
    ('en-us', _('English (US)')),
    ('pt-br', _('Português')),
)
# ============================= MIDDLEWARES ================================= #
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
# =========================== AUTH BACKENDS ================================= #
AUTHENTICATION_BACKENDS = [
    # auth
    'django.contrib.auth.backends.ModelBackend',
    # django-permission
    'permission.backends.PermissionBackend',
]
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    )
}
# ============================ VALIDATORS =================================== #
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.'
                'UserAttributeSimilarityValidator',
    },
]
# ========================= SERVER CONFIGURATION ============================ #
WSGI_APPLICATION = 'project.wsgi.application'

ALLOWED_HOSTS = ['*']
X_FRAME_OPTIONS = 'ALLOWALL'
XS_SHARING_ALLOWED_METHODS = ['POST', 'GET', 'OPTIONS', 'PUT', 'DELETE']

# Name of cache backend to cache user agents. If it not specified default
# cache alias will be used. Set to `None` to disable caching.
# Uncomment this when cache is configured
# USER_AGENTS_CACHE = 'default'

# ============================= TEMPLATES =================================== #
# Added to allow overriding django forms templates.
FORM_RENDERER = 'django.forms.renderers.TemplatesSetting'


class InvalidTemplateVariable(str):
    def __mod__(self, other):
        from django.template.base import TemplateSyntaxError
        # access to current settings
        from django.conf import settings

        # display the message on page in make log it only on stage development
        if settings.DEBUG is False:
            raise TemplateSyntaxError("Invalid variable : '{}'".format(other))


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'core', 'forms', 'templates'),
            os.path.join(BASE_DIR, 'frontend', 'templates'),
            os.path.join(BASE_DIR, 'gatheros_event', 'templates'),
            os.path.join(BASE_DIR, 'hotsite', 'templates'),
            os.path.join(BASE_DIR, 'mailer', 'templates'),
            os.path.join(BASE_DIR, 'bitly', 'templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            # 'string_if_invalid': InvalidTemplateVariable("%s"),
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.i18n',
                'project.context_processors.environment_version',
                'frontend.context_processors.render_app_only',
            ],
            'builtins': [
                'permission.templatetags.permissionif',
            ],
        },
    },
]
# ============================== LOGGING ==================================== #
# Disable
# LOGGING_CONFIG = None
#
# LOGGING = {
#     'version': 1,
#     'disable_existing_loggers': True,
#     'formatters': {
#         'verbose': {
#             'format': '%(levelname)s %(asctime)s %(module)s '
#                       '%(process)d %(thread)d %(message)s'
#         },
#     },
#     'handlers': {
#         'console': {
#             'level': 'DEBUG',
#             'class': 'logging.StreamHandler',
#             'formatter': 'verbose'
#         }
#     },
#     'loggers': {
#         'django.db.backends': {
#             'level': 'ERROR',
#             'handlers': ['console'],
#             'propagate': False,
#         },
#     },
# }
# ============================== FIXTURES =================================== #
FIXTURE_DIRS = [
    os.path.join(BASE_DIR, 'fixtures'),
    os.path.join(BASE_DIR, 'fixtures', 'workflows'),
]
# ============================= CKEDITOR ==================================== #
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
# ============================= MESSAGES ==================================== #
MESSAGE_TAGS = {
    message_constants.DEBUG: 'debug',
    message_constants.INFO: 'info',
    message_constants.SUCCESS: 'success',
    message_constants.WARNING: 'warning',
    message_constants.ERROR: 'danger',
}
# =============================== E-MAIL ==================================== #
DEFAULT_FROM_EMAIL = 'Congressy <mail@congressy.net>'
CONGRESSY_REPLY_TO = 'Congressy <congressy@congressy.com>'
DEV_ALERT_EMAILS = ['Infra Congressy <infra@congressy.com>']
SALES_ALERT_EMAILS = [
    'Wyndson Oliveira <wyndson@congressy.com>',
    'Infra Congressy <infra@congressy.com>'
]
# ============================ WKHTML PDF =================================== #
WKHTMLTOPDF_CMD = os.path.join(
    BASE_DIR, "bin", "wkhtmltox", "bin", 'wkhtmltopdf'
)

# =========================== CRON CLASSES ================================== #
ALLOW_PARALLEL_RUNS = True
FAILED_RUNS_CRONJOB_EMAIL_PREFIX = "[Server check]: "

CRON_CLASSES = [
    "payment.cron.MyCronJob",
]
# =============================== BITLY ===================================== #
BITLY_LOGIN = 'congressy'
BITLY_API_KEY = 'R_90819c7eac3f4c039e5f9c37f6786dda'
BITLY_ACCESS_TOKEN = '5e9398fb6cc39e8dee301f9c0192959563b8bd02'
# Tempo em que o relatório de cada link irá renovar os dados.
BITLY_TIMEOUT_STATS = 30
