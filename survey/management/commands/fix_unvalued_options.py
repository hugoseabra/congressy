from django.core.management.base import BaseCommand
from django.utils.text import slugify

from survey.models import Option


class Command(BaseCommand):
    help = 'Criar value para options vazios - remover comando após uso #752'

    def handle(self, *args, **options):
        err_options = Option.objects.filter(
            value__isnull=True,
        )

        self.stdout.write(self.style.ERROR(
            'Encontradas {} options sem value.'.format(err_options.count())
        ))

        for option in err_options:

            slughorn = slugify(option.name)

            existing_options = Option.objects.filter(
                question=option.question,
                value=slughorn,
            )

            if existing_options.count() >= 1:
                self.stdout.write(self.style.WARNING(
                    'Opção: {}, encontradas {} com o mesmo value'.format(
                        option.name,
                        existing_options.count())
                ))

                counter = 1

                for opt in existing_options:

                    query_set = Option.objects.filter(
                        value=slughorn + '-' + str(counter),
                        question=opt.question,
                    )

                    if query_set.exists():
                        counter += 1

                option.value = slughorn + '-' + str(counter)
                option.save()
                option.save()
                self.stdout.write(self.style.WARNING(
                    'Opção repetida: {}, salva com o value {}'.format(
                        option.name,
                        option.value)
                ))

            else:

                option.value = slughorn
                option.save()
                self.stdout.write(self.style.SUCCESS(
                    'Opção: {}, salva com o value {}'.format(option.name,
                                                             option.value)
                ))
