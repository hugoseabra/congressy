import sys

from django.core.management.base import BaseCommand

from addon.models import Service
from gatheros_subscription.models import LotCategory


class Command(BaseCommand):
    help = 'Copia serviços de uma categoria de evento para outra.'

    def add_arguments(self, parser):
        parser.add_argument('from_service_id', type=int)
        parser.add_argument('to_category_id', type=int)

    def handle(self, *args, **options):

        addon_pk = options.get('from_service_id')
        lot_category_pk = options.get('to_category_id')

        try:
            addon = Service.objects.get(pk=addon_pk)
            lot_category = LotCategory.objects.get(pk=lot_category_pk)

            if addon.lot_category.event != lot_category.event:
                self.stdout.write(self.style.ERROR(
                    'Categoria e Opcional não pertencem ao mesmo evento.'
                ))
                sys.exit(1)

            addon.pk = None
            addon.lot_category = lot_category
            addon.save()

            self.stdout.write(self.style.SUCCESS(
                'Cópia realizada com sucesso.'
            ))

        except Service.DoesNotExist:
            self.stdout.write(self.style.ERROR(
                'Opcional não encontrado. ID: {}'.format(addon_pk)
            ))
            sys.exit(1)

        except LotCategory.DoesNotExist:
            self.stdout.write(self.style.ERROR(
                'Categoria não encontrada. ID: {}'.format(lot_category_pk)
            ))
            sys.exit(1)
