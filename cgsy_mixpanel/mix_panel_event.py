from decimal import Decimal


class MixPanelEvent:
    """
    Objeto de valor do MixPanel para dados do evento.
    """

    def __init__(self,
                 identity: str,
                 name: str,
                 city_name: str,
                 state_name: str,
                 paid: bool,
                 transfer_tax: bool,
                 congressy_plan_percent: str,
                 ticket_amount_max: Decimal = None,
                 ticket_amount_min: Decimal = None,
                 ticket_amount_avg: Decimal = None):
        self.identity = identity
        self.name = name
        self.city_name = city_name
        self.state_name = state_name
        self.paid = paid
        self.transfer_tax = transfer_tax
        self.congressy_plan_percent = congressy_plan_percent
        self.ticket_amount_max = ticket_amount_max
        self.ticket_amount_min = ticket_amount_min
        self.ticket_amount_avg = ticket_amount_avg

        self.incremented_data = dict()

    def increment(self, key, value):
        self.incremented_data[key] = value

    def __iter__(self):
        iters = {
            'ID': self.identity,
            'Nome do evento': self.name,
            'Cidade': self.city_name,
            'Estado': self.city_name,
            'Pago': self.paid,
            'Transfere Taxa ao Participante': self.transfer_tax,
            'Plano Percentual Congressy': self.congressy_plan_percent,
            'Ticket Máximo': self.ticket_amount_max,
            'Ticket Mínimo': self.ticket_amount_min,
            'Ticket Médio': self.ticket_amount_avg,
        }

        iters.update(self.incremented_data)

        # now 'yield' through the items
        for x, y in iters.items():
            yield x, y
