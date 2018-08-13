from django.core.management.base import BaseCommand

from gatheros_event.models import Person


class Command(BaseCommand):
    help = 'Procurar por Users com emails duplicados'

    def handle(self, *args, **options):

        persons = Person.objects.all()
        user_emails = list()

        for person in persons:
            if not person.user:
                continue

            if person.user.email not in user_emails:
                user_emails.append(person.user.email)
            else:
                self.stdout.write(self.style.ERROR(
                    'Duplicate email: {}'.format(person.user.email)
                ))
