from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from core.cli.mixins import CliInteractionMixin
from gatheros_subscription.management.cmd_event_mixins import CommandEventMixin
from gatheros_subscription.models import Subscription


class Command(BaseCommand, CliInteractionMixin, CommandEventMixin):
    help = 'Cria usuário para participantes que ainda não possuem usuário.'

    def add_arguments(self, parser):
        parser.add_argument('event_id', type=int, nargs='?')
        parser.add_argument(
            '--force-internal',
            dest='force_internal',
            action='store_true',
            help='processar em simulação, mas sem executar na persistência.',
        )

    def handle(self, *args, **options):
        event = self._get_event(pk=options.get('event_id'))

        # Inscrições de pessoas não possuem usuário e que possuem e-mail
        subs_qs = Subscription.objects.filter(
            event_id=event.pk,
            test_subscription=False,
            status=Subscription.CONFIRMED_STATUS,
            person__user_id__isnull=True,
            person__email__isnull=False,
        )

        if options.get('force_internal', False) is False:
            subs_qs = subs_qs.filter(origin=Subscription.DEVICE_ORIGIN_MANAGE)

        subs_qs = subs_qs.order_by('person__email')

        self.stdout.write(self.style.SUCCESS(
            '# INSCRIÇÕES: {}'.format(subs_qs.count() or '0')
        ))

        existing_users = list()

        counter = 1
        for sub in subs_qs:
            person = sub.person
            names = person.name.strip().split(' ')
            if User.objects.filter(username=person.email).exists() is True:
                existing_users.append(sub)
                counter += 1
                continue

            user = User.objects.create_user(
                username=person.email,
                email=person.email,
                password=sub.code,
                first_name=str(names[0])[0:29],
                last_name=' '.join(names[1:])[0:29]
            )
            person.user = user
            person.save()

            self.stdout.write(self.style.SUCCESS(
                ' - {}. User "{}" created.'.format(counter, person.email)
            ))
            counter += 1

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(
            '# USUARIOS EXISTENTES: {}'.format(len(existing_users) or '0')
        ))
        counter = 1
        for sub in existing_users:
            person = sub.person
            self.stdout.write(self.style.WARNING(
                ' - {}. User "{}" already exists. Person: {}, Insc: {}'.format(
                    counter,
                    person.email,
                    person.pk,
                    sub.pk
                )
            ))
            counter += 1

