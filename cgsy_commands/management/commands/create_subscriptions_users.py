import sys

from django.core.management import call_command
from django.core.management.base import BaseCommand

from gatheros_subscription.models import Lot, LotCategory, Subscription


class Command(BaseCommand):
    help = 'Criar usuários (se não tiverem) de participantes de uma' \
           ' determinada categoria e lote e e enviar o e-mail de boas-vindas.'

    def add_arguments(self, parser):
        parser.add_argument(
            'event_id',
            help='ID do evento',
            type=int,
        )
        parser.add_argument(
            'cat_id',
            help='ID da categoria',
            type=int,
        )
        parser.add_argument('-l', '--lot_ids', type=int, nargs='+')

    def handle(self, *args, **options):

        try:
            sub_qs = Subscription.objects.filter(
                lot__category_id=options['cat_id'],
                event_id=options['event_id'],
                person__user_id__isnull=True,
            )

            lot_ids = options.get('lot_ids')

            if lot_ids:
                sub_qs = sub_qs.filter(lot_id__in=lot_ids)

            num = sub_qs.count()
            if num == 0:
                self.stderr.write('Nenhuma inscrição encontrada.')
                return

            self.stdout.write(self.style.SUCCESS(
                '{} insc. encontradas.'.format(num)
            ))

            sub = sub_qs.first()
            event = sub.event
            cat = sub.lot.category

            self.stdout.write(self.style.SUCCESS(
                'EVENTO: .'.format(event.name)
            ))
            self.stdout.write(self.style.SUCCESS(
                'CATEGORIA: .'.format(cat.name)
            ))

            if lot_ids:
                lots = Lot.objects.filter(pk__in=lot_ids)
                self.stdout.write(self.style.SUCCESS(
                    'LOTE(S): .'.format(cat.name)
                ))
                for lot in lots:
                    self.stdout.write(self.style.SUCCESS(
                        '  - {} ({})'.format(lot.name, lot.pk,)
                    ))

                print()

            self.stdout.write(self.style.SUCCESS(
                '{} insc. encontradas.'.format(num)
            ))

            confirmation = input("\nProcessar y/N:  ")

            possibilities = [
                'y',
                'yes',
                's',
                'sim',
            ]

            if confirmation.lower() not in possibilities:
                self.stdout.write(self.style.NOTICE(
                    "\n Exit!"
                ))
                sys.exit(0)

            for sub in sub_qs:
                person = sub.person.user

                call_command(
                    'create_subscription_user',
                    sub.pk,
                )


        except LotCategory.DoesNotExist:
            self.stderr.write("Categoria '{}' não encontrada.".format(uuid))
