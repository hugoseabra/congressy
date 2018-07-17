from django.core.management.base import BaseCommand

from gatheros_event.models import Event


class Command(BaseCommand):
    help = 'Atualiza contagem geral de inscritos nos eventos.'

    def handle(self, *args, **options):

        events = Event.objects.all()
        event_count = 0

        for event in events:

            count = 1
            has_subs = False

            for sub in event.subscriptions.all().order_by('created'):
                sub.event_count = count
                count += 1
                sub.save()
                has_subs = True

            if has_subs:
                event_count += 1
                self.stdout.write("  - {}: {} atualizados".format(
                    event.name,
                    self.style.SUCCESS(count-1)
                ))

        self.stdout.write(self.style.SUCCESS(
            'Updated events: {}'.format(event_count)
        ))
