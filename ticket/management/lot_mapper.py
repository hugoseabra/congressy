from datetime import datetime, timedelta

from core.util.date import DateTimeRange
from ticket.models import Ticket, Lot


class LotMapper:
    """
    Essa classe é responsavel por criar as novas estruturas necessarias para uma
    migração de dados pré 1.7.0 para pós 1.7.0.

    Para isso ela deve ser capaz de criar e mapear essas novas estruturas com as
    antigas para permitir que quem for consumir esses dados conheça seu contexto

    Então podemos dizer que essa classe deve:

        * Criar Ingressos
        * Criar novos Lots e mapear os antigos lotes com novos lots criados
    """

    def __init__(self, event, new_map=False, old_map=False) -> None:

        self.lots = event.lots.all()

        # Acumula datas de início e fim para verificação de conflito
        self.lot_dates = [
            {'ds': lot.date_start, 'de': lot.date_end, 'pk': lot.pk}
            for lot in self.lots
        ]

        if new_map is True:
            self.map_type = 'new_map'
        elif old_map is True:
            self.map_type = 'old_map'

        self.event = event

        self._transfer_tax()

    def create_map(self):
        if self.map_type == 'new_map':
            return self._create_new_map()
        elif self.map_type == 'old_map':
            return self._create_old_map()

    def _create_old_map(self):
        lots = self.event.lots.all()
        lot_map = dict()
        ticket_map = dict()
        count = 1

        if lots.count() == 0:
            # Event with no lots and no tickets

            ticket = Ticket.objects.create(
                event=self.event,
                name='Geral - #{}'.format(count),
            )
            count += 1

            Lot.objects.create(
                ticket=ticket,
                # name='Lote 1',
                date_start=self.event.date_start - timedelta(days=30),
                date_end=self.event.date_start - timedelta(minutes=1),
            )

            return lot_map

        for lot in lots:
            date_conflict = \
                self._has_date_conflict(lot.pk, lot.date_start, lot.date_end)

            if lot.category_id:

                if lot.category_id in ticket_map and date_conflict is False:
                    ticket = ticket_map[lot.category_id]

                else:
                    ticket, _ = Ticket.objects.get_or_create(
                        name=lot.category.name + " - #{}".format(count),
                        event=self.event,
                        active=lot.category.active,
                        paid=lot.price and lot.price > 0,
                    )

                    count += 1

                    ticket_map[lot.category_id] = ticket

            else:

                if self.event.pk in ticket_map and date_conflict is False:
                    ticket = ticket_map[self.event.pk]

                else:
                    ticket, _ = Ticket.objects.get_or_create(
                        event=self.event,
                        name='Geral - #{}'.format(count),
                        paid=lot.price and lot.price > 0,
                    )

                    count += 1

                    ticket_map[self.event.pk] = ticket

            if lot.event_survey_id:
                ticket.event_survey = lot.event_survey
                ticket.save()

            new_lot, _ = Lot.objects.get_or_create(
                # name=lot.name[0:79],
                date_start=lot.date_start,
                date_end=lot.date_end,
                ticket=ticket,
            )

            lot_map[lot.pk] = new_lot

            if lot.price:
                new_lot.price = lot.price
                new_lot.save()

        return lot_map

    def _create_new_map(self):
        lots = self.event.lots.all()
        lot_map = dict()
        ticket_map = dict()
        count = 1

        if lots.count() == 0:
            return lot_map

        for lot in lots:

            if lot.category:

                ticket_name = lot.category.name[:254]

                if ticket_name in ticket_map:
                    ticket_name = ticket_name + " - #{}".format(count)
                    count += 1

                ticket, _ = Ticket.objects.get_or_create(
                    event=self.event,
                    name=ticket_name,
                    active=lot.category.active,
                    limit=lot.limit,
                    free_installments=lot.num_install_interest_absortion,
                )

                ticket_map[ticket_name] = ticket

            else:

                ticket_name = lot.name[:254]
                if ticket_name in ticket_map:
                    ticket_name = ticket_name + " - #{}".format(count)
                    count += 1

                ticket, _ = Ticket.objects.get_or_create(
                    event=self.event,
                    name=ticket_name,
                    active=lot.active,
                    limit=lot.limit,
                    free_installments=lot.num_install_interest_absortion,
                )

                ticket_map[self.event.pk] = ticket

            if lot.event_survey:
                ticket.event_survey = lot.event_survey
                ticket.save()

            if lot.private and lot.exhibition_code:
                ticket.exhibition_code = lot.exhibition_code
                ticket.active = False
                ticket.save()

            nl, _ = Lot.objects.get_or_create(
                # name=lot.name[0:79],
                date_start=lot.date_start,
                date_end=lot.date_end,
                ticket=ticket,
            )

            lot_map[lot.pk] = nl

            if lot.price:
                ticket.paid = True
                nl.price = lot.price
                nl.save()
                ticket.save()

        return lot_map

    def _has_date_conflict(self, lot_pk, date_start: datetime,
                           date_end: datetime):

        session_range_one = DateTimeRange(start=date_start, stop=date_end)

        for lot_date_data in self.lot_dates:
            ds = lot_date_data['ds']
            de = lot_date_data['de']
            pk = lot_date_data['pk']

            if pk == lot_pk:
                continue

            session_range_two = DateTimeRange(start=ds, stop=de, )

            if date_start == ds or ds in session_range_one \
                    or date_start in session_range_two:
                return True

        return False

    def _transfer_tax(self):

        state = False

        for lot in self.lots:
            if lot.transfer_tax is True:
                state = True
                break

        if state is True:
            self.event.transfer_tax = True
            self.event.save()
