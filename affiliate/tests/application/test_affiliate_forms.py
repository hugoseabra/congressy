""" Testes de serviços de aplicação do módulo de Afiliados. """

from test_plus.test import TestCase

from affiliate import forms


class AffiliateFormTest(TestCase):
    """ Testa formulário de afiliado. """

    def test_render(self):
        form = forms.AffiliateForm()

        for field in form:
            print(field.name)

