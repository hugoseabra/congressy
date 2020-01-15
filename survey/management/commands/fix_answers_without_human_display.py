from ast import literal_eval
from datetime import date

from django.core.management.base import BaseCommand
from django.db.models import Q
from django.db.models.functions import Lower
from django.utils.text import slugify

from survey.models import Question, Option


class Command(BaseCommand):
    help = 'Corrige valor de human display de respostas.'

    def handle(self, *args, **options):

        for question in Question.objects.all():
            has_options = question.has_options is True

            for answer in question.answers.filter(human_display__isnull=True):
                answer_value = answer.value

                is_slugfied = (' ' in answer_value) is False

                human_display = self.get_human_display(
                    question,
                    answer_value,
                )

                if has_options:
                    answer_value = slugify(answer_value)
                    answer.value = answer_value

                print('Answer: {} - {} - {}'.format(
                    answer.pk,
                    answer_value,
                    human_display,
                ))

                answer.human_display = human_display
                answer.save()

    def get_human_display(self, question: Question, answer_value: str):
        """
        Resgata exibição humana da resposta.
        - Se data, formatação com data
        - Se lista, valores separados por víncula conforme exibido no
          formulário;
        - Se entrada manual, exibir conforme foi inserido no formulário.
        """
        q_type = question.type

        if question.type == Question.FIELD_INPUT_DATE:
            if not isinstance(answer_value, date):
                return answer_value

            return answer_value.strftime('%d/%m/%Y')

        if q_type in (Question.FIELD_SELECT, Question.FIELD_RADIO_GROUP):

            try:
                option = question.options.get(
                    Q(value=slugify(answer_value)) |
                    Q(name__contains=answer_value.lower())
                )
                return option.name

            except Option.DoesNotExist:
                return answer_value

        elif q_type == Question.FIELD_CHECKBOX_GROUP:
            try:
                answer_value = literal_eval(str(answer_value))

                if not isinstance(answer_value, list):
                    # tem de ser uma lista
                    answer_value = [answer_value]

                human_display_items = []
                for item in answer_value:
                    try:
                        option = question.options.get(
                            Q(value=slugify(item)) |
                            Q(name__contains=item.lower())
                        )
                        human_display_items.append(option.name)

                    except Option.DoesNotExist:
                        pass

                return ', '.join(human_display_items)

            except(ValueError, SyntaxError):
                pass

        return answer_value
