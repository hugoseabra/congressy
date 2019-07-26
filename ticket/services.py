from base.services import ApplicationService
from ticket import managers


class TicketService(ApplicationService):
    manager_class = managers.TicketManager


class TicketLotService(ApplicationService):
    manager_class = managers.LotManager
