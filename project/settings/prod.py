# pylint: skip-file

from . import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'cgsy',
        'USER': 'cgsy',
        'PASSWORD': 'CgsyAdmin!@#qwe',
        'PORT': 5432,
        'HOST': 'postgres',  # Docker host
    },
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'

# Congressy -> conforme configuração na conta do SparkPost
EMAIL_HOST = 'smtp.sparkpostmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'SMTP_Injection'
EMAIL_HOST_PASSWORD = '6dacd78f4c49080da7bbe942d4f36dc95d0c110a'
EMAIL_USE_TLS = True
CONGRESSY_EMAIL_SENDER = 'mail@congressy.net'
CONGRESSY_REPLY_TO = 'congressy@congressy.com'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
