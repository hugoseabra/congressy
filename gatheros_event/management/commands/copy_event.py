from django.core.management.base import BaseCommand
from django.db.transaction import atomic

from core.cli.mixins import CliInteractionMixin
from gatheros_subscription.management.cmd_event_mixins import CommandEventMixin


class Command(BaseCommand, CliInteractionMixin, CommandEventMixin):
    help = 'Copia eventos para uma mesma organização'

    def add_arguments(self, parser):
        parser.add_argument('event_id', type=int, nargs='?')
        parser.add_argument('event_name', type=str, nargs='?')

    def handle(self, *args, **options):
        event = self._get_event(pk=options.get('event_id'))

        event_name = options.get('event_name')
        if event_name:
            event.name = event_name

        event.slug = None

        print('==============================================================')

        info = event.info
        lots = event.lots.all()

        with atomic():
            event.pk = None
            event.save()

            event_lot = event.lots.first()

            info.pk = None
            info.event_id = event.pk
            info.save()

            lot = lots.first()

            event_lot.name = lot.name
            event_lot.date_start = lot.date_start
            event_lot.date_end = lot.date_end
            event_lot.price = lot.price
            event_lot.transfer_tax = lot.transfer_tax
            event_lot.num_install_interest_absortion = \
                lot.num_install_interest_absortion
            event_lot.private = lot.private
            event_lot.exhibition_code = lot.exhibition_code
            event_lot.allow_installment = lot.allow_installment
            event_lot.installment_limit = lot.installment_limit
            event_lot.active = lot.active
            event_lot.save()

            cat = lot.category
            event_cat = event.lot_categories.first()
            event_cat.name = cat.name
            event_cat.save()

            self.stdout.write(
                self.style.SUCCESS('Evento criado: {}'.format(event.pk))
            )
            self.stdout.write(
                self.style.SUCCESS(
                    'Organização: {}'.format(event.organization.name)
                )
            )
