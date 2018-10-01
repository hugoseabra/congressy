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

        for err in err_options:
            self._create_slug(err, err.name, err.question)

    def _create_slug(self, option, name, question):
        """
            Slugify deve garantir que o nome de Option em uma Question seja
            único.
        """

        original_slug = slugify(name)

        slug = original_slug

        self.stdout.write(self.style.WARNING(
            'Tentando: {}'.format(slug)
        ))

        existing_options = Option.objects.filter(
            value=original_slug,
            question=question,
        )

        self.stdout.write(self.style.WARNING(
            'Encontradas {}!'.format(existing_options.count())
        ))

        if existing_options.count() >= 1:
            counter = 1
            for option in existing_options:

                query_set = Option.objects.filter(
                    value=option.value,
                    question=question,
                )

                if query_set.exists():
                    slug = original_slug + '-' + str(counter)
                    counter += 1

        option.value = slug
        option.save()
        self.stdout.write(self.style.SUCCESS(
            'Opção: {}, salva com o value {}'.format(option.name, option.value)
        ))
