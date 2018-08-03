from django.core.management.base import BaseCommand

from gatheros_subscription.models import EventSurvey
from survey.models import Author, Question


class Command(BaseCommand):
    help = 'Cria a entidade SubscriptionAuthor para respostas ' \
           'que não estão vinculadas'

    def handle(self, *args, **options):

        event_surveys = EventSurvey.objects.all()

        all_subs_count = 0
        needs_processing_count = 0
        has_sub_author_count = 0
        author_not_found_count = 0
        author_found_count = 0

        author_not_found_list = list()
        event_with_author_not_found_list = list()

        for event_survey in event_surveys:

            event = event_survey.event

            all_subs_in_event = event.subscriptions.all()

            for sub in all_subs_in_event:

                es = sub.lot.event_survey
                user = sub.person.user

                if es is not None and \
                        self.has_any_required_questions(es.survey):

                    all_subs_count += 1

                    if sub.author is not None:
                        has_sub_author_count += 1
                    else:
                        try:
                            Author.objects.get(
                                user=user,
                                survey=es.survey,
                            )
                            author_found_count += 1
                        except Author.DoesNotExist:

                            event = sub.event
                            if event not in event_with_author_not_found_list:
                                event_with_author_not_found_list.append(event)

                            author_not_found_list.append({
                                'user': user,
                                'survey': es.survey,
                                'event': sub.event,
                            })

                            author_not_found_count += 1

                        needs_processing_count += 1

        self.stdout.write(self.style.SUCCESS(
            '\nSubs with event survey count: {}\n'
            'Needs processing count: {}\n'
            'Author found count: {}\n'
            'Has existing authors counts: {}\n'.format(
                all_subs_count,
                needs_processing_count,
                author_found_count,
                has_sub_author_count,
            )
        ))

        self.stdout.write(self.style.ERROR(
            '\nERRORS:\n'
            'Author not found count: {}\n'.format(
                author_not_found_count,
            )
        ))

        for item in author_not_found_list:
            self.stdout.write(self.style.ERROR(
                '\nNOT FOUND :\n'
                'User: {}\n'
                'Event: {}\n'
                'Survey: {}\n\n'.format(
                    item['user'],
                    item['event'],
                    item['survey'],
                )
            ))

        self.stdout.write(self.style.ERROR(
            '\nEVENTS WITH NO AUTHOR FOUND\n'
        ))
        for item in event_with_author_not_found_list:
            self.stdout.write(self.style.ERROR(
                '\n {}'.format(item.name)
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
