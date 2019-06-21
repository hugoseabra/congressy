# pylint: skip-file
#############################################################################
# CUIDADO!!!
# A configuração de banco de dados é gerada automaticamente pelo deploy.
# Não mude as configurações de DATABASES.
#############################################################################

from .prod import *

# ================================= APPS ==================================== #
INSTALLED_APPS.extend([
    'sync_client',
])
