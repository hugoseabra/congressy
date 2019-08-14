from django.core.management.base import BaseCommand
from django.db.models import Count
from django.db.transaction import atomic

from core.cli.mixins import CliInteractionMixin
from gatheros_subscription.models import EventSurvey, Subscription


class Command(BaseCommand, CliInteractionMixin):
    def handle(self, *args, **options):
        event_surveys = EventSurvey.objects.annotate(
            num_answers=Count('survey__questions__answers'),
        ).filter(
            num_answers__gt=0,
        ).order_by('pk')

        num_event_surveys = event_surveys.count() or 1

        self.stdout.write(self.style.SUCCESS('Event surveys: {}'.format(
            num_event_surveys or '0'
        )))

        ev_survey_counter = 0

        self.progress_bar(
            ev_survey_counter,
            num_event_surveys,
            prefix='Event Survey (#{}):'.format(ev_survey_counter),
            suffix='Complete',
            length=50
        )

        # autores que serão transeridos
        to_transfer = list()

        # autores que tem potencial de serem transferidos. Vamos apenas
        # validar outros formulários, para se os campos batem.
        potential_to_transfer = list()

        # evitar ciclicidade
        sub_pks = list()

        for ev_survey in event_surveys:

            from_event = ev_survey.event
            from_survey = ev_survey.survey

            # Autores do evento de origem
            from_authors = from_survey.authors.annotate(
                num_answers=Count('answers')
            ).filter(
                num_answers__gt=0,
            )

            # Peristência de nome aguardando o próximo autor para registra-lo
            wait_for_next = list()

            for from_author in from_authors:
                if not from_author.user_id and not hasattr(from_author,
                                                           'subscription'):
                    # author não está vinculada a nada. Vamos ignorar
                    continue

                if from_author.user_id and hasattr(from_author.user, 'person'):
                    person = from_author.user.person
                    subs_qs = person.subscriptions

                    if subs_qs.filter(
                            event_id=from_event.pk).exists() is False:
                        # Pessoa tem inscrição  no próprio evento de origem?
                        to_transfer.append({
                            'from_event': from_event,
                            'from_ev_survey': ev_survey,
                            'from_author': from_author,
                        })
                    elif hasattr(from_author, 'subscription'):
                        sub = from_author.subscription
                        if sub.event_id != from_event.pk:
                            # Incrição do autor não é a inscrição de origem.
                            to_transfer.append({
                                'from_event': from_event,
                                'from_ev_survey': ev_survey,
                                'from_author': from_author,
                            })

                        else:
                            # mesmo sendo do mesmo evento, vamos aguardar re-
                            # incidência.
                            if person.pk not in wait_for_next:
                                # se não é diferente, a inscrição é do próprio
                                # evento
                                wait_for_next.append(person.pk)
                                continue

                            potential_to_transfer.append({
                                'sub': sub,
                                'from_ev_survey': ev_survey,
                                'from_author': from_author,
                            })

                    else:
                        subs = subs_qs.exclude(
                            pk__in=sub_pks,
                            event_id=from_event.pk,
                        )

                        if subs.count() == 0:
                            # Não há outras inscrições
                            continue

                        if person.pk not in wait_for_next:
                            wait_for_next.append(person.pk)

                        else:
                            for sub in subs:
                                sub_pks.append(str(sub.pk))
                                # a partir da aqui, já existe mais de um autor para
                                # para a mesma pessoa no mesmo evento, vamos setar
                                # como potencial de transferência.
                                potential_to_transfer.append({
                                    'sub': sub,
                                    'from_ev_survey': ev_survey,
                                    'from_author': from_author,
                                })

            ev_survey_counter += 1
            self.progress_bar(
                ev_survey_counter,
                num_event_surveys,
                prefix='Event Survey (#{}):'.format(ev_survey_counter),
                suffix='Complete',
                length=50
            )

        self.process_to_transfer(to_transfer)
        self.process_potential_to_transfer(potential_to_transfer)

    def process_to_transfer(self, to_transfer: list):

        print()
        self.stdout.write('Processando autores garantidos de transferência')

        self.stdout.write(self.style.SUCCESS('Authors to transfer: {}'.format(
            len(to_transfer) or '0'
        )))

        if len(to_transfer):
            to_transfer_counter = 0
            self.progress_bar(
                to_transfer_counter,
                len(to_transfer),
                prefix='Authors (#{}):'.format(to_transfer_counter),
                suffix='Complete',
                length=50
            )

        events_to_check_surveys = dict()

        sub_pks = list()

        for item in to_transfer:
            from_event = item['from_event']
            from_ev_survey = item['from_ev_survey']
            from_author = item['from_author']

            if not from_author.user_id:
                continue

            user = from_author.user

            if not hasattr(user, 'person'):
                continue

            person = user.person

            for sub in person.subscriptions.all():

                if str(sub.pk) in sub_pks:
                    continue

                event = sub.event

                if event.surveys.count() == 0:
                    sub_pks.append(str(sub.pk))
                    continue

                if event.pk not in events_to_check_surveys:
                    events_to_check_surveys[event.pk] = {
                        'event': event,
                        'surveys': [ev_s.survey for ev_s in
                                    event.surveys.all()],
                        'sub': sub,
                        'authors': list()
                    }

                events_to_check_surveys[event.pk]['authors'].append({
                    'author': from_author,
                    'question_names': sorted([
                        a.question.name
                        for a in from_author.answers.all()
                    ]),
                })
                sub_pks.append(str(sub.pk))

            to_transfer_counter += 1
            self.progress_bar(
                to_transfer_counter,
                len(to_transfer) or 1,
                prefix='Authors (#{}):'.format(to_transfer_counter),
                suffix='Complete',
                length=50
            )

        self.check_and_transfer_authors(events_to_check_surveys)

        print()

    def process_potential_to_transfer(self, potential_to_transfer: list):
        print(potential_to_transfer)

    def check_and_transfer_authors(self, authors_to_check: dict):

        total_authors_to_check = len(authors_to_check.keys())

        self.stdout.write(self.style.SUCCESS('Eventos para checar: {}'.format(
            total_authors_to_check or '0'
        )))

        num_authors_to_check = 0

        if num_authors_to_check:
            num_authors_to_check = 0
            self.progress_bar(
                num_authors_to_check,
                total_authors_to_check,
                prefix='Checking ev (#{}):'.format(num_authors_to_check),
                suffix='Complete',
                length=50
            )

        with atomic():
            for _, item in authors_to_check.items():
                event = item['event']

                for survey in item['surveys']:
                    question_names = \
                        sorted([q.name for q in survey.questions.all()])

                    for item_author in item['authors']:
                        if question_names == item_author['question_names']:
                            author = item_author['author']
                            sub_exists = Subscription.objects.filter(
                                person__user_id=author.user_id,
                                event_id=event.pk,
                            ).exclude(
                                person__user__authors__surve_id=survey.pk,
                            ).exists()

                            if sub_exists:
                                # compatível
                                author.survey = survey
                                author.save()

                num_authors_to_check += 1

                self.progress_bar(
                    num_authors_to_check,
                    total_authors_to_check,
                    prefix='Checking ev (#{}):'.format(
                        num_authors_to_check),
                    suffix='Complete',
                    length=50
                )
