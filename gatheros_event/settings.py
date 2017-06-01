# pylint: skip-file
from django.conf import settings

"""
Periodo em dias apartir da realização do convite que ele ficará disponível
"""
INVITATION_ACCEPT_DAYS = getattr(settings, 'INVITATION_ACCEPT_DAYS ', 6)
