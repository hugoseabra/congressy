import os

from django.core.management.base import BaseCommand

from addon.models import Service
from core.cli.mixins import CliInteractionMixin
from gatheros_subscription.management.cmd_event_mixins import CommandEventMixin
from gatheros_subscription.models import Subscription
from project.manage import settings


class Command(BaseCommand, CliInteractionMixin, CommandEventMixin):
    help = 'Relatório de Atividades Extras por tag.'

    def add_arguments(self, parser):
        parser.add_argument('event_id', type=int, nargs='?')
        parser.add_argument('tags', type=str, nargs='?')

    def handle(self, *args, **options):

        tag_opts = None
        if options.get('tags'):
            tag_opts = options.get('tags').split(',')

        event = self._get_event(pk=options.get('event_id'))
        tags = self._get_tag(tags=tag_opts)

        print('==============================================================')
        addons = Service.objects.filter(
            lot_category__event_id=event.pk,
            tag__in=tags,
        ).order_by('tag', 'schedule_start')

        lines = [
            ["ID", "nome", "tema", "num. inscricoes"]
        ]

        for addon in addons:
            subs_qs = addon.subscription_services.filter(
                subscription__completed=True,
                subscription__test_subscription=False,
            ).exclude(
                subscription__status=Subscription.CANCELED_STATUS,
            )

            line = [
                str(addon.pk),
                addon.name,
                addon.theme.name,
                str(subs_qs.count()),
            ]
            print("{}. {} ({}): {}".format(*line))

            lines.append(line)

        file_name = '{}_{}_{}.csv'.format(event.pk, event.slug, "-".join(tags))

        print()
        with open(os.path.join(settings.BASE_DIR, file_name), 'w') as f:
            for line in lines:
                f.write(";".join(line) + "\n")

        f.close()
        self.stdout.write(
            "Arquivos salvo em: {}".format(self.style.SUCCESS(os.path.join(
                settings.BASE_DIR,
                file_name,
            )))
        )
        print()

    def _get_tag(self, tags: list = None):

        while not tags:
            if not tags:
                self.stdout.write("\n")
                self.stdout.write(
                    "Informe o identificador único (ou encerre com Ctrl+c)")
                tags_str = input("Tag: ")
                if tags_str:
                    tags = [tag.strip() for tag in tags_str.split(',')]

        return list(set([tag.upper() for tag in tags]))
