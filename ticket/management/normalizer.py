from addon.models import Service, Product
from gatheros_subscription.models import Subscription
from payment.models import Transaction
from ticket.management import Base
from ticket.models import Lot


class Normalizer(Base):
    """
    Essa classe é responsavel por normalizar/migrar dados da versão pré 1.7.0
    para versão pós 1.7.0 dado um evento e um mapeamento de lotes ela deve:

        * Migrar as inscrições
        * Migrar as transações
        * Migrar os formularios personalizados(survey)
        * Migrar os opcionais(serviços e e produtos)

    """

    def __init__(self, event, lot_map, *args, **kwargs):
        self.event = event
        self.lot_map = lot_map
        super().__init__(*args, **kwargs)

    def subscriptions(self):
        self.stdout.write(
            self.style.SUCCESS(
                'Normalizando inscrições do evento {} ({})...'
                ''.format(self.event.name, self.event.pk)
            )
        )

        subscriptions = Subscription.objects.filter(
            event_id=self.event.pk,
        )

        for subscription in subscriptions:

            if subscription.lot_id in self.lot_map.keys():
                ticket_lot = self.lot_map[subscription.lot_id]
            elif subscription.event_id in self.lot_map.keys():
                ticket_lot = self.lot_map[subscription.event_id]
            else:

                msg = "Nenhum ticket encontrado para inscrição {} com lot_id " \
                      "{} e event_id {}\n".format(
                    str(subscription.pk),
                    subscription.lot.id,
                    subscription.event.id,
                )

                self.stderr.write(self.style.ERROR(msg))

                with open('errs.txt', 'a+') as f:
                    f.write(msg)
                continue

            assert isinstance(ticket_lot, Lot)

            subscription.ticket_lot = ticket_lot
            subscription.save()

        self.stdout.write(
            self.style.SUCCESS(
                'Normalização das inscrições: OK'
            )
        )

    def transactions(self):
        self.stdout.write(
            self.style.SUCCESS(
                'Normalizando transações do evento {} ({})...'
                ''.format(self.event.name, self.event.pk)
            )
        )

        subscriptions = Subscription.objects.filter(
            event_id=self.event.pk,
        )

        for subscription in subscriptions:
            transactions = subscription.transactions.all()
            for transaction in transactions:

                if subscription.lot_id in self.lot_map.keys():
                    ticket_lot = self.lot_map[subscription.lot_id]
                elif subscription.event_id in self.lot_map.keys():
                    ticket_lot = self.lot_map[subscription.event_id]
                else:

                    msg = "Nenhum ticket encontrado para insc {}  e " \
                          "transação {} com lot_id {} e event_id {}\n".format(
                        str(subscription.pk),
                        transaction.pk,
                        subscription.lot.id,
                        subscription.event.id,
                    )

                    with open('errs.txt', 'a+') as f:
                        f.write(msg)

                    self.stderr.write(self.style.ERROR(msg))
                    continue

                Transaction.objects.filter(
                    pk=transaction.pk,
                ).update(
                    ticket_lot=ticket_lot
                )

        self.stdout.write(
            self.style.SUCCESS(
                'Normalização das transações: OK'
            )
        )

    def surveys(self):
        self.stdout.write(
            self.style.SUCCESS(
                'Normalizando formulários personalizados do evento {} ({})...'
                ''.format(self.event.name, self.event.pk)
            )
        )

        for lot in self.event.lots.all():

            if lot.event_survey:

                try:
                    ticket_lot = self.lot_map[lot.pk]
                except KeyError:
                    ticket_lot = self.lot_map[lot.event_id]

                ticket = ticket_lot.ticket

                ticket.event_survey = lot.event_survey
                ticket.save()

        self.stdout.write(
            self.style.SUCCESS(
                'Normalização dos formulários personalizados: OK'
            )
        )

    def addons(self):
        self.stdout.write(
            self.style.SUCCESS(
                'Normalizando addons do evento {}...'.format(self.event.name)
            )
        )

        for lot in self.event.lots.all():

            try:
                ticket_lot = self.lot_map[lot.pk]
            except KeyError:
                ticket_lot = self.lot_map[self.event.pk]

            Service.objects.filter(
                lot_category=lot.category
            ).update(
                ticket=ticket_lot.ticket,
            )

            Product.objects.filter(
                lot_category=lot.category
            ).update(
                ticket=ticket_lot.ticket,
            )

        self.stdout.write(
            self.style.SUCCESS(
                'Normalização dos addons: OK'
            )
        )

    def normalize(self):
        self.subscriptions()
        self.transactions()
        self.surveys()
        self.addons()
