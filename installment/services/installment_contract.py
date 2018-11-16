from base import services
from installment import managers


class InstallmentContractService(services.ApplicationService):
    """ Application service. """
    manager_class = managers.InstallmentContractManager
