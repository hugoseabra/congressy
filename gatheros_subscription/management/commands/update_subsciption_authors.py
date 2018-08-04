from django.core.management.base import BaseCommand

from gatheros_subscription.models import EventSurvey
from survey.models import Author, Question


class Command(BaseCommand):
    help = 'Cria a entidade SubscriptionAuthor para respostas ' \
           'que não estão vinculadas'

    def handle(self, *args, **options):

        event_surveys = EventSurvey.objects.all()

        needs_processing_count = 0

        for event_survey in event_surveys:

            event = event_survey.event

            all_subs_in_event = event.subscriptions.all().filter(
                completed=True,
                test_subscription=False,
            )

            for sub in all_subs_in_event:

                es = sub.lot.event_survey
                user = sub.person.user

                if es is not None and \
                        self.has_any_required_questions(es.survey):

                    if sub.author is None:
                        try:
                            sub.author = Author.objects.get(
                                user=user,
                                survey=es.survey,
                            )
                            sub.save()
                            needs_processing_count += 1

                        except Author.DoesNotExist:
                            pass

        self.stdout.write(self.style.SUCCESS(
            '\nProcessed: {}\n'.format(
                needs_processing_count,
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
