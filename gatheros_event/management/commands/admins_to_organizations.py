from django.core.management.base import BaseCommand

from gatheros_event.models import Member, Organization
from django.contrib.auth.models import User
from django.db.models import Count


class Command(BaseCommand):
    help = 'Inserir super administradores e todas as organizações possuem' \
           ' eventos.'

    def handle(self, *args, **options):
        admin_users = User.objects.filter(is_superuser=True,
                                          person__isnull=False)
        for user in admin_users:
            person = user.person
            orgs = Organization.objects.annotate(
                num_events=Count('events')
            ).filter(num_events__gt=0).exclude(members__person=person)

            self.stdout.write(self.style.SUCCESS(
                'Orgs found for {}: {}'.format(user.first_name, orgs.count())
            ))

            for org in orgs:
                Member.objects.create(
                    person_id=person.pk,
                    organization_id=org.pk,
                    group=Member.ADMIN,
                )
                self.stdout.write(self.style.SUCCESS(
                    '   - Member created: {} on {}'.format(
                        person.name,
                        org.name
                    )
                ))
