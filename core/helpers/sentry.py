import logging

try:
    from raven.contrib.django.raven_compat.models import client

    SENTRY_RAVEN = True
except ImportError:
    SENTRY_RAVEN = False


def log(message, extra_data=None, type='error', notify_admins=False):
    logger = logging.getLogger(__name__)

    if type == 'error':
        logger.error(message, extra=extra_data)
        if SENTRY_RAVEN:
            client.captureMessage(message, **extra_data)

    if type == 'warning':
        logger.warning(message, extra=extra_data)

        if notify_admins is True and SENTRY_RAVEN:
            client.captureMessage(message, **extra_data)

    if type == 'message':
        logger.info(message, extra=extra_data)

        if notify_admins is True and SENTRY_RAVEN:
            client.captureMessage(message, **extra_data)
