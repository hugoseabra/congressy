"""
Testes de domínio do módulo Survey conforme documentação.
"""

from django.test import TestCase


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
