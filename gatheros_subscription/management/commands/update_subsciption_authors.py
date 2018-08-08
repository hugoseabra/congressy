from django.core.management.base import BaseCommand

from gatheros_subscription.models import EventSurvey
from survey.models import Author, Question


class Command(BaseCommand):
    help = 'Cria a entidade SubscriptionAuthor para respostas ' \
           'que não estão vinculadas'

    def handle(self, *args, **options):

        event_surveys = EventSurvey.objects.all()

        processing_count = 0
        total_subs = 0
        total_created = 0
        total_existing = 0

        for event_survey in event_surveys:

            event = event_survey.event

            all_subs_in_event = event.subscriptions.all().filter(
                author__isnull=True,
                lot__event_survey__isnull=False,
            )
            num_subs = len(all_subs_in_event)

            if not num_subs:
                continue

            self.stdout.write(self.style.SUCCESS(
                '# ================ Subs: {}'.format(len(all_subs_in_event))
            ))

            for sub in all_subs_in_event:

                user = sub.person.user

                if not user:
                    continue

                es = sub.lot.event_survey
                total_subs += 1

                self.stdout.write(self.style.SUCCESS(
                    'Processing: {}'.format(
                        sub.pk,
                    )
                ))

                created = False
                try:
                    author = Author.objects.get(
                        user=user,
                        survey=es.survey,
                    )

                except Author.DoesNotExist:
                    author = Author.objects.create(
                        user=user,
                        survey=es.survey
                    )
                    created = True

                sub.author = author
                sub.save()

                processing_count += 1

                if created:
                    total_created += 1
                else:
                    total_existing += 1

        self.stdout.write(self.style.SUCCESS(
            '\nTotal Processed: {}'.format(
                processing_count,
            )
        ))
        self.stdout.write(self.style.SUCCESS(
            '\nCreated {} new authors!'.format(
                total_created,
            )
        ))

        self.stdout.write(self.style.SUCCESS(
            '\nAssociated {} existing authors to their subscription'.format(
                total_existing,
            )
        ))

        self.stdout.write(self.style.SUCCESS(
            '\nTotal subscriptions: {}'.format(
                total_subs,
            )
        ))

    @staticmethod
    def has_any_required_questions(survey):

        questions = Question.objects.filter(
            survey=survey
        )

        for question in questions:
            if question.required:
                return True
        return False
