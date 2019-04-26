from core.util.collection import merge_lists_ignore_duplicates
from gatheros_event.models import Person, Member
from django.contrib.auth.models import User
from .base import DataCleanerBase


class PersonDataCleaner(DataCleanerBase):

    # noinspection PyMethodMayBeStatic
    def erase(self, event_pk):
        members = [
            str(m.person.pk)
            for m in
            Member.objects.filter(organization__events=event_pk)
        ]

        subscribed_people = [
            str(p.pk)
            for p in
            Person.objects.filter(subscriptions__event_id=event_pk)
        ]

        ids = merge_lists_ignore_duplicates(members, subscribed_people)

        qs = Person.objects.all().exclude(pk__in=ids)

        uqs = User.objects.all().exclude(person__pk__in=ids)

        msg = 'Deleting {} from {}'.format(uqs.count(),
                                           User._meta.label)

        if self.stdout and self.style:
            self.stdout.write(self.style.SUCCESS(
                msg
            ))
        else:
            print(msg)

        msg = 'Deleting {} from {}'.format(qs.count(),
                                           Person._meta.label)

        if self.stdout and self.style:
            self.stdout.write(self.style.SUCCESS(
                msg
            ))
        else:
            print(msg)

        qs.delete()
