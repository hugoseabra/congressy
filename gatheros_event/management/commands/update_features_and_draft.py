from django.core.management.base import BaseCommand

from gatheros_event.helpers.event_business import is_paid_event, is_free_event
from gatheros_event.helpers.publishing import event_is_publishable
from gatheros_event.models import Event, FeatureManagement, FeatureConfiguration


class Command(BaseCommand):
    help = 'Ajustar eventos antigos para usarem a nova infra de features'

    def handle(self, *args, **options):
        i = 0

        for event in Event.objects.all():
            self.stdout.write(self.style.SUCCESS(
                'Configuring: {}'.format(event.name)
            ))

            config = FeatureConfiguration.objects.create(
                event=event,
                feature_certificate=True,
                feature_internal_subscription=True,
                feature_checkin=True,
                feature_multi_lots=True,
                feature_survey=True,
                feature_products=True,
                feature_services=True,
            )

            management = FeatureManagement.objects.create(
                event=event,
                certificate=True,
                checkin=True,
                survey=True,
                products=True,
                services=True,
            )

            management.save()
            config.save()

            if is_paid_event(event):
                event.business_status = \
                    event.EVENT_BUSINESS_STATUS_PAID
            elif is_free_event(event):
                event.business_status = \
                    event.EVENT_BUSINESS_STATUS_FREE
            else:
                raise Exception('Unknown event state')

            event.published = event_is_publishable(event)

            event.save()

            i += 1

        self.stdout.write(self.style.SUCCESS(
            '\nProcessed: {} events'.format(i)
        ))
