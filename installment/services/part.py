from base import services
from installment import managers


class PartService(services.ApplicationService):
    """ Application service. """
    manager_class = managers.PartManager
