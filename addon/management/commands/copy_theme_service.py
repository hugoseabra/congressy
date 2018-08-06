import sys

from django.core.management.base import BaseCommand

from addon.models import Service, Theme


class Command(BaseCommand):
    help = 'Copia serviços de uma categoria de evento para outra.'

    def add_arguments(self, parser):
        parser.add_argument('from_service_id', type=int)
        parser.add_argument('to_theme_id', type=int)

    def handle(self, *args, **options):

        addon_pk = options.get('from_service_id')
        to_theme_pk = options.get('to_theme_id')

        try:
            addon = Service.objects.get(pk=addon_pk)
            theme = Theme.objects.get(pk=to_theme_pk)

            if addon.lot_category.event != theme.event:
                self.stdout.write(self.style.ERROR(
                    'Categoria e Serviço não pertencem ao mesmo evento.'
                ))
                sys.exit(1)

            addon.pk = None
            addon.theme = theme
            addon.save()

            self.stdout.write(self.style.SUCCESS(
                'Cópia realizada com sucesso.'
            ))

        except Service.DoesNotExist:
            self.stdout.write(self.style.ERROR(
                'Serviço não encontrado. ID: {}'.format(addon_pk)
            ))
            sys.exit(1)

        except Theme.DoesNotExist:
            self.stdout.write(self.style.ERROR(
                'Grupo temático não encontrado. ID: {}'.format(to_theme_pk)
            ))
            sys.exit(1)
