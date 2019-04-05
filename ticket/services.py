from base.services import ApplicationService
from ticket import managers


class TicketService(ApplicationService):
    manager_class = managers.TicketManager


class LotService(ApplicationService):
    manager_class = managers.LotManager
