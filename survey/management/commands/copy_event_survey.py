import sys

from django.core.management.base import BaseCommand
from django.db.transaction import atomic

from core.cli.mixins import CliInteractionMixin
from core.util.commands import progress_bar
from gatheros_event.models import Event
from gatheros_subscription.models import EventSurvey
from survey.models import Survey


class Command(BaseCommand, CliInteractionMixin):
    help = 'Copiar um formulário personalizado de um evento para o outro.'

    def handle(self, *args, **options):

        self.stdout.write(self.style.WARNING("EVENTO DE ORIGEM"))
        from_event = self._get_event()
        self.stdout.write("\n")

        self.stdout.write(self.style.WARNING("EVENTO DE DESTINO"))
        to_event = self._get_event()

        self.stdout.write("\n\n")
        self.stdout.write(self.style.SUCCESS(from_event.name))
        self.stdout.write(self.style.SUCCESS('=' * len(from_event.name)))
        self.stdout.write("\n")

        self.stdout.write("... para ...")

        self.stdout.write("\n")
        self.stdout.write(self.style.SUCCESS(to_event.name))
        self.stdout.write(self.style.SUCCESS('=' * len(to_event.name)))
        self.stdout.write("\n")

        self.confirmation_yesno("Continuar?", exit_on_false=True)

        survey = self.get_survey(from_event)

        self.copy(survey, to_event)

    def _get_event(self):
        event = None

        while not event:
            self.stdout.write("\n")
            self.stdout.write("Informe o evento (ou encerre com Ctrl+c)")
            event_pk = input("Event PK: ")

            try:
                event = self.get_event_instance(event_pk)

            except Exception:
                event_pk = None
                event = None

        return event

    def get_event_instance(self, event_pk):
        try:
            event = Event.objects.get(pk=event_pk)

            self.stdout.write('----------------------------------------------')
            if len(event.name) > 20:
                self.stdout.write('EVENT: ' + event.name[:20] + '...')
            else:
                self.stdout.write('EVENT: ' + event.name)

            org = event.organization

            if len(org.name) > 20:
                self.stdout.write('ORG: ' + org.name[:20] + '...')
            else:
                self.stdout.write('ORG: ' + org.name)

            return event

        except Event.DoesNotExist:
            raise Exception()

    def get_survey(self, event: Event):

        survey_qs = event.surveys.all()

        if survey_qs.count() == 0:
            self.stdout.write(self.style.WARNING(
                "\nEste evento não possui formulário personalizado."
            ))
            return sys.exit(1)

        self.report('Formulários', survey_qs.count())
        self.stdout.write("\n")

        survey_list = list()

        for event_survey in survey_qs.all():
            survey = event_survey.survey

            survey_list.append(
                ('{} (ID: {}) - Perguntas: {}'.format(
                    survey.name,
                    survey.pk,
                    survey.questions.count(),
                ),
                 survey)
            )

        selected_survey = self.choice_list(
            'survey_pk',
            'Selecione um formulário personalizado:',
            survey_list,
        )

        return selected_survey['survey_pk']

    def copy(self, survey: Survey, event: Event):

        self.stdout.write(self.style.SUCCESS(
            "Formulário: {} (ID: {}) - Perguntas: {}".format(
                survey.name,
                survey.pk,
                survey.questions.count(),
            )
        ))

        self.confirmation_yesno("Continuar?", exit_on_false=True)

        self.stdout.write("\n")

        total_artifacts = 0

        # questions
        questions = list()

        for q in survey.questions.all():
            total_artifacts += 1

            if q.has_options:
                options = q.options.all()
                total_artifacts += options.count()
            else:
                options = list()

            q.pk = None
            questions.append({
                'question': q,
                'options': options
            })

        progress_bar(
            0,
            total_artifacts,
            prefix='Progress:',
            suffix='Complete',
            length=40
        )

        processed_artifacts = 0
        with atomic():
            survey.pk = None
            survey.save()

            EventSurvey.objects.create(event_id=event.pk, survey_id=survey.pk)

            for item in questions:
                question = item['question']
                question.survey_id = survey.pk

                question.save()

                options = item['options']

                for o in options:
                    o.pk = None
                    o.question_id = question.pk
                    o.save()

                    processed_artifacts += 1

                    progress_bar(
                        processed_artifacts,
                        total_artifacts,
                        prefix='Progress:',
                        suffix='Complete',
                        length=40
                    )

                processed_artifacts += 1

                progress_bar(
                    processed_artifacts,
                    total_artifacts,
                    prefix='Progress:',
                    suffix='Complete',
                    length=40
                )

    def report(self, key, value, separator=': ', topic='- '):
        self.stdout.write('{}{}{} '.format(topic, key, separator),
                          ending=False)
        self.stdout.write(str(value), style_func=self.style.SUCCESS)
