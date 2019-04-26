from base import services
from installment import managers


class ContractService(services.ApplicationService):
    """ Application service. """
    manager_class = managers.ContractManager
