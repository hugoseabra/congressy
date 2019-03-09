from django.core.management.base import BaseCommand
from django.core.management import call_command

from gatheros_subscription.models import LotCategory, Subscription


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

            for sub in sub_qs:
                person = sub.person.user

                call_command(
                    'create_subscription_user',
                    sub.pk,
                )


        except LotCategory.DoesNotExist:
            self.stderr.write("Categoria '{}' não encontrada.".format(uuid))
