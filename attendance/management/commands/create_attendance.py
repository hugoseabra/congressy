from datetime import datetime

from django.core.management.base import BaseCommand

from gatheros_subscription.models import Subscription
from attendance.models import AttendanceService, Checkin


class Command(BaseCommand):
    help = 'Atualiza as inscrições que estão com dados de attendance ' \
           'ainda vinculados a inscrição'

    accepts = [
        'y',
        'yes',
        'sim',
        's',
    ]

    event_pk = 213
    event_start = datetime(year=2018, month=9, day=22)
    manual_checkin_time = datetime(year=2018,
                                   month=9,
                                   day=22,
                                   hour=9,
                                   minute=30)

    def handle(self, *args, **options):

        subscriptions = Subscription.objects.filter(
            event_id=self.event_pk,
            attended=True,
        )

        self.stdout.write(self.style.SUCCESS(
            'Encontradas {} inscrições com attended == True'
            ' '.format(subscriptions.count())
        ))

        process = str(input("Deseja realmente processar essas inscrições? "
                            "Y/N [N]: ") or "n")

        if process in self.accepts:
            attendance_service = AttendanceService.objects.create(
                event_id=self.event_pk,
            )

            for sub in subscriptions:
                self.stdout.write(self.style.SUCCESS(
                    'Processando inscrição: {}'
                    ' '.format(sub.pk)
                ))
                checkin = Checkin.objects.create(
                    created_by="Nathan (Congressy)",
                    created_on=self.manual_checkin_time,
                    attendance_service_id=attendance_service.pk,
                    subscription=sub
                )
                self.stdout.write(self.style.SUCCESS(
                    'Criado checkin: {}\n'.format(checkin.pk)
                ))

    def handle_manual_subscriptions(self):

        # Treat manual subscriptions
        manual_only_subscriptions = Subscription.objects.filter(
            event_id=self.event_pk,
            origin=Subscription.DEVICE_ORIGIN_MANAGE,
        )

        self.stdout.write(self.style.SUCCESS(
            'Encontradas {} inscrições com DEVICE_ORIGIN_MANAGE == manage '
            ' '.format(manual_only_subscriptions.count())
        ))

        manual_subscriptions = Subscription.objects.filter(
            event_id=self.event_pk,
            created__gt=self.event_start,
            origin=Subscription.DEVICE_ORIGIN_MANAGE,
            attended=False,
        )

        self.stdout.write(self.style.SUCCESS(
            'Encontradas {} inscrições com que ocorram no dia do evento e'
            ' sem atendimentos'
            ' '.format(manual_subscriptions.count())
        ))

        process_manuals = str(input("Deseja realmente processar inscrições "
                                    "manuais? Y/N [N]: ") or "n")

        if process_manuals in self.accepts:

            for sub in manual_subscriptions:
                self.stdout.write(self.style.SUCCESS(
                    'Processando inscrição: {}'
                    ' '.format(sub.pk)
                ))

                sub.attended = True
                sub.attended_on = self.manual_checkin_time
                sub.save()
