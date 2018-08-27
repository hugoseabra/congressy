from django.core.management.base import BaseCommand
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
            )

            management = FeatureManagement.objects.create(
                event=event,
                certificate=True,
                checkin=True,
            )

            if event.has_survey:
                management.survey = True
                config.feature_survey = True

            if event.has_checkin:
                management.checkin = True
                config.feature_checkin = True

            if event.has_extra_activities:
                management.services = True
                config.feature_services = True

            if event.has_optionals:
                management.products = True
                config.feature_products = True

            management.save()
            config.save()

            i += 1

        self.stdout.write(self.style.SUCCESS(
            '\nProcessed: {} events'.format(i)
        ))
