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
                completed=True,
                test_subscription=False,
            )

            for sub in all_subs_in_event:

                es = sub.lot.event_survey
                user = sub.person.user
                total_subs += 1

                self.stdout.write(self.style.SUCCESS(
                    'Processing: {}'.format(
                        sub.pk,
                    )
                ))

                if es is not None and \
                        self.has_any_required_questions(es.survey):

                    if sub.author is None:
                        author, created = Author.objects.get_or_create(
                            user=user,
                            survey=es.survey,
                        )
                        sub.author = author
                        # sub.save()
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
