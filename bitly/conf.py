from django.conf import settings

BITLY_TIMEOUT_STATS = getattr(settings, 'BITLY_TIMEOUT_STATS', 30)
