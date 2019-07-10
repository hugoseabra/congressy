from django.core.management.base import BaseCommand

from addon.models import SubscriptionService
from addon.services import SubscriptionServiceService
from gatheros_subscription.models import Subscription


class Command(BaseCommand):
    help = 'Libera vagas de atividades extras.'

    def add_arguments(self, parser):
        parser.add_argument('min_days_release', type=int, nargs='?')

    def handle(self, *args, **options):

        min_days = options.get('min_days_release')

        if min_days:
            self.stdout.write('Tolerância em até {} dias'.format(
                self.style.SUCCESS(min_days)
            ))

        addon_subs = SubscriptionService.objects.exclude(
            subscription__status__in=[
                Subscription.CONFIRMED_STATUS,
                Subscription.CANCELED_STATUS,
            ]
        )

        self.stdout.write(
            self.style.SUCCESS(str(addon_subs.count())) + ' encontrados.'
        )
        count_released = 0

        for addon_sub in addon_subs:
            service = SubscriptionServiceService(instance=addon_sub)
            if service.release_optional(min_days) is True:
                count_released += 1

        self.stdout.write(
            self.style.SUCCESS(str(count_released)) + ' liberados.'
        )
