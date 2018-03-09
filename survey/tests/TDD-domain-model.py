"""
Testes de domínio do módulo Survey conforme documentação.
"""

from django.test import TestCase


class SurveyQuestionTest(TestCase):
    """
    Testes de Model de Pergunta
    """
    def question_unique_in_survey(self):
        """ Testa se pergunta é única em um formulário. """
        self.fail('not implmented')


class SurveyOptionTest(TestCase):
    """
    Testes de Model de Opção de perguntas
    """
    def option_of_selectable_question(self):
        """ Testa se opção é de um campo com suporte a opções. """
        self.fail('not implmented')

    def option_unique_in_question(self):
        """ Testa se valor de opção é único para o campo. """
        self.fail('not implmented')


class SurveyAnswerTest(TestCase):
    """
    Testes de Model de Resposta
    """
    def answer_with_output_when_selectable_question(self):
        """
        Testa se resposta de uma pergunta com suporte a opções sempre possui
        saída de valor para o usuário (human_display).
        """
        self.fail('not implmented')
