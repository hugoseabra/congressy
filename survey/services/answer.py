"""
    Serviço de Aplicação para Respostas
"""
from ast import literal_eval
from datetime import date

from survey.managers import AnswerManager
from survey.models import Question, Option
from survey.services import mixins


class AnswerService(mixins.ApplicationServiceMixin):
    """ Application Service """
    manager_class = AnswerManager

    def _get_manager_kwargs(self, **kwargs):
        kwargs = super()._get_manager_kwargs(**kwargs)
        data = kwargs.get('data')
        if data:
            data.update({'human_display': self._get_human_display(
                data.get('question'),
                data.get('value'),
            )})
            kwargs.update({'data': data})

        return kwargs

    @staticmethod
    def _get_human_display(question_pk, value):
        """
        Resgata exibição humana da resposta.
        - Se data, formatação com data
        - Se lista, valores separados por víncula conforme exibido no
          formulário;
        - Se entrada manual, exibir conforme foi inserido no formulário.
        """

        if not question_pk or not value:
            # manager will handle the error
            return None

        try:
            question = Question.objects.get(pk=question_pk)
        except Question.DoesNotExist:
            return value

        if question.type == Question.FIELD_INPUT_DATE:
            if not isinstance(value, date):
                return value

            return value.strftime('%d/%m/%Y')

        if question.type == Question.FIELD_SELECT \
                or question.type == Question.FIELD_RADIO_GROUP:

            try:
                option = question.options.get(value=value)
                return option.name

            except Option.DoesNotExist:
                return value

        if question.type == Question.FIELD_CHECKBOX_GROUP:
            try:
                value = literal_eval(str(value))
                if not isinstance(value, list):
                    # tem de ser uma lista
                    return value

                human_display_items = []
                for item in value:
                    try:
                        option = question.options.get(value=item)
                        human_display_items.append(option.name)

                    except Option.DoesNotExist:
                        pass

                return ', '.join(human_display_items)

            except(ValueError, SyntaxError):
                return value

        return value
