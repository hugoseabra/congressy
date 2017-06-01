# test_transferir_evento_para_outra_organizacao_do_administrador(self):
from datetime import datetime, timedelta
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class EventEditDateViewTest(TestCase):
    fixtures = [
        '003_occupation',
        '005_user',
        '006_person',
        '007_organization',
        '008_member',
        'kanu_locations_city_test',
        '004_category',
        '007_organization',
        '009_place',
        '010_event',
    ]

    def setUp(self):
        self.user = User.objects.get(username="lucianasilva@gmail.com")
        self.client.force_login(self.user)
        self.url = reverse(
            'gatheros_event:event-edit-dates',
            kwargs={'pk': 4}
        )
        self.url_success = reverse(
            'gatheros_event:event-panel',
            kwargs={'pk': 4}
        )
        self.data = {
            'date_start': datetime.now() + timedelta(days=5),
            'date_end': datetime.now() + timedelta(days=5, hours=6),
        }

    def test_get_ok(self):
        """
        Retornar a página com o formulário deve ser ok
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_invalid_date_start(self):
        """
        Data inicial inválida devem retornar erro
        """
        # noinspection PyTypeChecker
        self.data.update({'date_start': 'foo/bar'})
        response = self.client.post(self.url, self.data)
        self.assertContains(
            response,
            "Informe uma data/hora válida."
        )

    def test_invalid_date_end(self):
        """
        Data final inválida devem retornar erro
        """
        # noinspection PyTypeChecker
        self.data.update({'date_end': 'foo/bar'})
        response = self.client.post(self.url, self.data)
        self.assertContains(
            response,
            "Informe uma data/hora válida."
        )

    def test_success_post_shoud_redirect(self):
        """
        Tudo certo deve redirecionar para o painel
        """
        response = self.client.post(self.url, self.data)
        self.assertRedirects(response, self.url_success)
