"""
Testes de domínio do módulo Survey conforme documentação.
"""

from django.test import TestCase


class SurveyQuestionTest(TestCase):
    """
    Testes de ModelForm para Pergunta
    """

    def question_unique_in_survey_prefix(self):
        """
        Testa se pergunta com um nome repetido no formulário é salvo com
        sucesso inserindo um prefixo e mantendo a unicidade.
        """
        self.fail('not implmented')


class SurveyOptionTest(TestCase):
    """
    Testes de ModelForm de Opção de perguntas
    """

    def question_unique_in_survey_prefix(self):
        """
        Testa se opção com um valor repetido na pergunta é salva com sucesso
        inserindo um prefixo e mantendo a unicidade.
        """
        self.fail('not implmented')


class SurveyAnswerTest(TestCase):
    """
    Testes de ModelForm para Resposta
    """
    def answer_unique_if_user(self):
        """
        Testa se o usuário, ao submenter respostas de um formulário que ele
        já tenha respondido anteriormente, possui as respostas anteriores
        editadas, não gerando novas respostas.
        """
        self.fail('not implmented')
