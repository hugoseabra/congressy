from django.core.management.base import BaseCommand
from django.db.models import Count
from django.db.transaction import atomic

from core.cli.mixins import CliInteractionMixin
from gatheros_subscription.management.cmd_event_mixins import CommandEventMixin


class Command(BaseCommand, CliInteractionMixin, CommandEventMixin):
    help = 'Relatório de Atividades Extras por tag.'

    def add_arguments(self, parser):
        parser.add_argument('event_id', type=int, nargs='?')

    def handle(self, *args, **options):
        event = self._get_event(pk=options.get('event_id'))

        category = None
        addon_choices = list()

        while category is None:
            categories = [
                ('{} - {}'.format(c.pk, c.name), c)
                for c in event.lot_categories.all()
            ]
            select_cat = self.choice_list('category', "Qual categoria?",
                                          categories)
            category = select_cat.get('category')

            if category.service_optionals.count():
                addon_choices.append(('Atividades extras', 'service'))

            if category.product_optionals.count():
                addon_choices.append(('Opcionais', 'product'))

            if not addon_choices:
                category = None

        select_addon = self.choice_list(
            "addon_type",
            "Que tipo de processamento?",
            addon_choices
        )
        addon_type = select_addon.get('addon_type')

        if addon_type == 'service':
            self.process_services(category)

        else:
            self.process_products(category)

    def process_services(self, category):

        addons_qs = category.service_optionals.annotate(
            num_subs=Count('subscription_services')
        ).filter(num_subs__gt=0)

        if addons_qs.count() == 0:
            self.stdout.write("Categoria não possui atividades extras.")
            self.exit()

        addons = [
            (
                "{}. {}... - {} insc - {} vagas".format(
                    a.pk,
                    a.name[:20],
                    a.subscription_services.count(),
                    a.quantity,
                ),
                a
            )
            for a in addons_qs.all().order_by('pk')
        ]
        select_from = self.choice_list('from', "Atividade extra de origem?",
                                       addons)
        from_addon = select_from.get('from')

        if from_addon.subscription_services.count() == 0:
            self.stdout.write("Sem inscrições para transferir.")
            self.exit()

        self.stdout.write("=========================================")
        self.stdout.write(self.style.SUCCESS(
            "Atividade origem: {}... (ID {}): {} insc. - {} vagas".format(
                from_addon.name[:20],
                from_addon.pk,
                from_addon.subscription_services.count(),
                from_addon.quantity,
            )
        ))
        self.stdout.write("=========================================")

        if addons_qs.exclude(pk=from_addon.pk).count() == 0:
            self.stdout.write("Nenhum destino disponível.")
            self.exit()

        addons = [
            (
                "{}. {}... - {} insc - {} vagas".format(
                    a.pk,
                    a.name[:20],
                    a.subscription_services.count(),
                    a.quantity,
                ),
                a
            )
            for a in addons_qs.exclude(pk=from_addon.pk).order_by('pk')
        ]
        select_to = self.choice_list('to', "Atividade extra de destino?",
                                     addons)
        to_addon = select_to.get('to')

        self.stdout.write("=========================================")
        self.stdout.write(self.style.SUCCESS(
            "Atividade destino: {}... (ID {}): {} insc. - {} vagas".format(
                to_addon.name[:20],
                to_addon.pk,
                to_addon.subscription_services.count(),
                to_addon.quantity,
            )
        ))
        self.stdout.write("=========================================")

        self.transfer_subscriptions(from_addon, to_addon)

    def process_products(self, category):

        addons_qs = category.product_optionals

        if addons_qs.count() == 0:
            self.stdout.write("Categoria não possui opcionais.")
            self.exit()

        addons = [(a.name, a) for a in addons_qs.all()]
        select_from = self.choice_list('from', "Opcional de origem?",
                                       addons)
        from_addon = select_from.get('from')

        self.stdout.write("=========================================")
        self.stdout.write(self.style.SUCCESS(
            "Opcional {} (ID {}): {} insc. - {} vagas".format(
                from_addon.name,
                from_addon.pk,
                from_addon.subscription_services.count() or "0",
                from_addon.quantity,
            )
        ))
        self.stdout.write("=========================================")

        print(from_addon.name)

    def transfer_subscriptions(self, addon_from, addon_to):
        num_subs_from = addon_from.subscription_services.count()
        num_subs_to = addon_to.subscription_services.count()

        if num_subs_from + num_subs_to > addon_to.quantity:
            self.stdout.write(
                "Número de inscrições ultrapassa limite de vagas do destino."
            )
            self.exit()

        self.stdout.write("=========================================")
        self.stdout.write(self.style.SUCCESS(
            "ID: {}: {} insc. - {} vagas".format(
                addon_from.pk,
                num_subs_from or "0",
                addon_from.quantity,
            )
        ))
        print()
        self.stdout.write("... para ...")
        print()
        self.stdout.write(self.style.SUCCESS(
            "ID: {}: {} insc. - {} vagas".format(
                addon_to.pk,
                num_subs_to or "0",
                addon_to.quantity,
            )
        ))
        self.stdout.write("=========================================")

        print()
        self.confirmation_yesno('Confirma a transferência?')

        counter = 0

        self.progress_bar(
            counter,
            num_subs_from,
            prefix='Progress:',
            suffix='Complete',
            length=50
        )

        sub_pks = [
            asub.subscription.pk
            for asub in addon_to.subscription_services.all()
        ]

        with atomic():
            for addon_sub in addon_from.subscription_services.all():

                if addon_sub.subscription_id in sub_pks:
                    addon_sub.delete()
                    continue

                addon_sub.optional_id = addon_to.pk
                addon_sub.save()
                counter += 1

                self.progress_bar(
                    counter,
                    num_subs_from,
                    prefix='Progress:',
                    suffix='Complete',
                    length=50
                )
