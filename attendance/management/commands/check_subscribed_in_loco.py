from datetime import timedelta

from django.core.management.base import BaseCommand, CommandError
from django.db.models import Count

from attendance.models import AttendanceService, Checkin
from core.util.commands import progress_bar
from gatheros_event.models import Event
from gatheros_subscription.models import Subscription


class Command(BaseCommand):
    help = 'Faz checkin de todos os inscritos a partir da data inicial do' \
           ' evento.'

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)
        parser.add_argument(
            '--dry-run',
            dest='dry',
            action='store_true',
            help='processar em simulação, mas sem executar na persistência.',
        )

        parser.add_argument(
            '--noinput',
            action='store_false',
            dest='interactive',
            default=True,
            help='Processar SEM interação com usuário.'
        )

        parser.add_argument(
            '-e',
            '--user',
            action='store',
            dest='event_pk',
            default=None,
            help='ID do evento.'
        )

        parser.add_argument(
            '-s',
            '--service',
            action='store',
            dest='service_pk',
            default=None,
            help='ID do evento.'
        )

    def handle(self, *args, **options):
        if args:
            raise CommandError(
                "check_subscribed_in_loco não possui argumentos."
            )

        dry = options['dry'] is True
        interact = options['interactive']

        event = self._get_event(**options)

        if interact:
            self.stdout.write("\n\n")
            self.stdout.write(self.style.SUCCESS(event.name))
            self.stdout.write(self.style.SUCCESS('=' * len(event.name)))
            self.stdout.write("\n")

        subs_qs = event.subscriptions.filter(
            completed=True,
            test_subscription=False,
            origin=Subscription.DEVICE_ORIGIN_MANAGE,
        )

        if subs_qs.count() == 0:
            if interact:
                self.stdout.write(self.style.WARNING(
                    "\nEste evento não possui inscrições."
                ))
            return

        if interact:
            self.report('Inscrições', subs_qs.count())

        in_loco_sub_qs = subs_qs.annotate(
            num_checkins=Count('checkins')
        ).filter(
            created__gte=event.date_start - timedelta(minutes=45),
            num_checkins=0,
            checkins__checkout__isnull=True,
        )

        if in_loco_sub_qs.count() == 0:
            if interact:
                self.stdout.write(self.style.WARNING(
                    "\nEste evento não possui inscrições no local que já não"
                    " estejam confirmadas."
                ))
            return

        if interact:
            self.report('Inscrições in-loco', in_loco_sub_qs.count())

        services_qs = event.attendance_services.all()

        if services_qs.count() == 0:
            if interact:
                self.stdout.write(self.style.WARNING(
                    "\nEste evento não atendimentos de check-in/out."
                ))
            return

        if interact:
            self.report('Serviços de atendimento', services_qs.count())

        for serv in services_qs:
            if interact:
                self.report(
                    '',
                    '{} ({})'.format(serv.name, serv.pk),
                    separator='',
                    topic='    -'
                )

        service = self._get_service(event, **options)

        checkins_qs = service.checkins.filter(
            checkout__isnull=True,
        )

        checked_subs_pks = [c.subscription_id for c in checkins_qs]
        not_checked_subs_qs = in_loco_sub_qs.exclude(pk__in=checked_subs_pks)

        if not_checked_subs_qs.count() == 0:
            if interact:
                self.stdout.write(self.style.WARNING(
                    "\nTodas as inscrições in-loco já foram confirmadas."
                ))
            return

        if interact:
            self.report('Inscrições confirmadas', checkins_qs.count())
            self.report(
                'Inscrições a confirmar',
                not_checked_subs_qs.count()
            )

        num_subs = not_checked_subs_qs.count()

        if interact:
            self.stdout.write("\n")
            progress_bar(
                0,
                num_subs,
                prefix='Progress:',
                suffix='Complete',
                length=40
            )

        counter = 1
        for sub in in_loco_sub_qs:
            Checkin.objects.create(
                attendance_service=service,
                subscription=sub,
            )
            if interact:
                progress_bar(
                    counter,
                    num_subs,
                    prefix='Progress:',
                    suffix='Complete',
                    length=40
                )
            counter += 1

    def _get_event(self, interactive, event_pk, **_):
        if interactive is False and not event_pk:
            if not event_pk:
                raise Exception('Evento não inforamdo.')

        event = None

        while not event:
            self.stdout.write("\n")
            if interactive is True and not event_pk:
                self.stdout.write("Informe o evento (ou encerre com Ctrl+c)")
                event_pk = input("Event PK: ")

            try:
                event = self.get_event_instance(event_pk, interactive)

            except Exception:
                event_pk = None
                event = None

                if interactive is False:
                    raise Exception('Evento não encontrado.')

        return event

    def get_event_instance(self, event_pk, interactive=True):
        try:
            event = Event.objects.get(pk=event_pk)

            if interactive is False:
                return event

            self.stdout.write('----------------------------------------------')
            if len(event.name) > 20:
                self.stdout.write('EVENT: ' + event.name[:20] + '...')
            else:
                self.stdout.write('EVENT: ' + event.name)

            org = event.organization

            if len(org.name) > 20:
                self.stdout.write('ORG: ' + org.name[:20] + '...')
            else:
                self.stdout.write('ORG: ' + org.name)

            self.stdout.write('----------------------------------------------')
            confirm = input(
                "É este o evento que deseja processar?"
                " Digite 'sim' para continue, or 'nao' para selecionar"
                " outro: """
            )

            if confirm.upper() not in ['SIM', 'YES']:
                self.stdout.write(self.style.ERROR('Escolha outro evento.'))
                event = None
                raise Exception()

            return event


        except Event.DoesNotExist:
            if interactive is False:
                self.stdout.write(self.style.ERROR('Evento não encontrado.'))
            raise Exception()

    def _get_service(self, event, interactive, service_pk, **_):
        if interactive is False and not service_pk:
            if not service_pk:
                raise Exception('Serviço de atendimento não inforamdo.')

        service = None

        while not service:
            self.stdout.write("\n")
            if interactive is True and not service_pk:
                self.stdout.write("Informe o serviço de atendimento:")
                service_pk = input("Service PK: ")

            try:
                service = self.get_service_instance(
                    event.pk,
                    service_pk,
                    interactive
                )

            except Exception as e:
                service_pk = None
                service = None

                if interactive is False:
                    raise Exception('Serviço de atendimento não encontrado.')

        return service

    def get_service_instance(self, event_pk, service_pk, interactive=True):
        try:
            service = AttendanceService.objects.get(
                pk=service_pk,
                event_id=event_pk
            )

            if interactive is False:
                return service

            self.stdout.write('----------------------------------------------')
            if len(service.name) > 20:
                self.stdout.write('SERVICE: ' + service.name[:20] + '...')
            else:
                self.stdout.write('SERVICE: ' + service.name)
            self.stdout.write('----------------------------------------------')

            return service


        except AttendanceService.DoesNotExist:
            if interactive is False:
                self.stdout.write(self.style.ERROR(
                    'Serviço de atendimento não encontrado.'
                ))
            raise Exception()

    def report(self, key, value, separator=': ', topic='- '):
        self.stdout.write('{}{}{} '.format(topic, key, separator),
                          ending=False)
        self.stdout.write(str(value), style_func=self.style.SUCCESS)
