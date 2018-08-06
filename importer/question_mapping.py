"""
    Essa classe representa um mapeamento de uma pergunta, com
    as opções que ela permite
"""

from survey.models import Question, Option


class QuestionMapping(object):

    def __init__(self, question: Question) -> None:

        if not isinstance(question, Question):
            raise ValueError('question não é do tipo Question')

        self.question = question                    
        self.name = question.label.lower().strip()
        self.description = question.help_text if question.help_text else ''
        self.description = self.description.lower()

        self.is_required = question.required
        self.options = self._get_options()

    def _get_options(self) -> list:
        options = list()
        all_options = Option.objects.filter(
            question=self.question,
        )

        for option in all_options:
            options.append(option.name.lower())

        return options
