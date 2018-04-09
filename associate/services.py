from associate import managers
from base import services


class AssociateService(services.ApplicationService):
    """ Application service de associado. """
    manager_class = managers.AssociateManager
