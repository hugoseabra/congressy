"""
Testes de aplicação do módulo Survey conforme documentação.
"""

from django.test import TestCase


class OptionTest(TestCase):
    """
    Testes de ModelForm de Opção de perguntas
    """
    def first_blank_option(self):
        """
        Testa opçaõ do usuário quando ele decide ter o primeiro a primeira
        opção em branco.
        """
        self.fail('not implmented')

    def option_of_selectable_question(self):
        """ Testa se opção é de um campo com suporte a opções. """
        self.fail('not implmented')
