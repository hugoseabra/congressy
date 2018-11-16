from base import services
from installment import managers


class InstallmentPartService(services.ApplicationService):
    """ Application service. """
    manager_class = managers.InstallmentPartManager
