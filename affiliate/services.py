from affiliate import managers
from base import services


class AffiliateService(services.ApplicationService):
    """ Application service de afiliado. """
    manager_class = managers.AffiliateManager


class AffiliationService(services.ApplicationService):
    """ Application service de afiliação. """
    manager_class = managers.AffiliationManager
