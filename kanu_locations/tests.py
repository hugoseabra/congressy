from django.test import TestCase, Client
from django.core.urlresolvers import reverse
from kanu_datatable.viewset import qs_to_dict


class CityTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('city-list')

    def get(self, data=None):
        aux = data or {}
        aux.update({'format': 'json'})
        return self.client.get(self.url, data).json()

    def test_campos_retorno(self):
        response = self.get()
        self.assertTrue('result' in response.keys())
        self.assertTrue('draw' in response.keys())
        self.assertTrue('recordsTotal' in response.keys())
        self.assertTrue('recordsFiltered' in response.keys())
        self.assertTrue('next' in response.keys())
        self.assertTrue('results' in response.keys())

    def test_campo_draw(self):
        response = self.get({'draw': 1})
        self.assertEqual(int(response['draw']), 1)

        response = self.get({'draw': 0})
        self.assertEqual(int(response['draw']), 0)

    def test_campo_length(self):
        response = self.get({'length': 5})
        self.assertEqual(len(response['results']), 5)

        response = self.get({'length': 10})
        self.assertEqual(len(response['results']), 10)

        response = self.get({'length': 7})
        self.assertEqual(len(response['results']), 7)

    def test_pesquisa_global(self):
        q = {'length': 10, 'search[value]': 'ABADIA D'}
        response = self.get(q)
        self.assertEqual(len(response['results']), 2)

    def test_pesquisa_global_acento(self):
        q = {'length': 10, 'search[value]': 'GOIÂNIA'}
        response = self.get(q)
        self.assertEqual(len(response['results']), 3)

    def test_pesquisa_colunas_name_uf(self):

        q = {
            'columns[2][data]': 'name',
            'columns[2][search][value]': 'ABADIA D',
            'columns[3][data]': 'uf',
            'columns[3][search][value]': 'MG',
        }
        response = self.get(q)
        self.assertEqual(len(response['results']), 1)
        self.assertEqual(response['results'][0]['name'], 'ABADIA DOS DOURADOS')
        self.assertEqual(response['results'][0]['uf'], 'MG')

    def test_nao_pesquisa_nada(self):
        q = {
            'columns[1][data]': 'id',
            'columns[1][orderable]': False,
            'columns[1][search][regex]': False,
            'columns[1][searchable]': True,
            'columns[2][data]': 'name',
            'columns[2][orderable]': True,
            'columns[2][search][regex]': False,
            'columns[2][searchable]': 'true',
        }
        response = self.get(q)
        self.assertGreater(len(response['results']), 0)

    def test_pesquisa_coluna_name(self):
        q = {
            'columns[2][data]': 'name',
            'columns[2][search][value]': 'ABADIA D',
        }
        response = self.get(q)
        self.assertEqual(len(response['results']), 2)
        states = (response['results'][0]['uf'], response['results'][1]['uf'])
        self.assertTrue('MG' in states)
        self.assertTrue('GO' in states)

    def test_campo_recordsFiltered(self):
        q = {'length': 10, 'search[value]': 'GOIÂNIA'}
        response = self.get(q)
        self.assertEqual(response['recordsFiltered'], 3)

    def test_campo_order(self):
        q = {
            'search[value]': 'ABADIA D',
            'columns[2][data]': 'name',
            'columns[3][data]': 'uf',
            'order[0][column]': '2',
            'order[0][dir]': 'asc',
            'order[1][column]': '3',
            'order[1][dir]': 'asc',
        }

        # name asc, uf asc
        response = self.get(q)
        name0 = response['results'][0]['name']
        name1 = response['results'][1]['name']
        self.assertLess(name0, name1, 'Ordenação não foi executada')

        # name desc, uf asc
        q = {
            'search[value]': 'ABADIA D',
            'columns[2][data]': 'name',
            'columns[3][data]': 'uf',
            'order[0][column]': '2',
            'order[0][dir]': 'desc',
            'order[1][column]': '3',
            'order[1][dir]': 'asc',
        }
        response = self.get(q)
        name0 = response['results'][0]['name']
        name1 = response['results'][1]['name']
        self.assertGreater(name0, name1, 'Ordenação não foi executada')

        # uf asc, name asc
        q = {
            'search[value]': 'ABADIA D',
            'columns[2][data]': 'name',
            'columns[3][data]': 'uf',
            'order[0][column]': '3',
            'order[0][dir]': 'asc',
            'order[1][column]': '2',
            'order[1][dir]': 'asc',
        }
        response = self.get(q)
        uf0 = response['results'][0]['uf']
        uf1 = response['results'][1]['uf']
        self.assertLess(uf0, uf1, 'Ordenação não foi executada')

        # uf desc, name asc
        q.update({
            'order[0][column]': '3',
            'order[0][dir]': 'desc',
        })
        response = self.get(q)
        uf0 = response['results'][0]['uf']
        uf1 = response['results'][1]['uf']
        self.assertGreater(uf0, uf1, 'Ordenação não foi executada')


class QueryStringToDictTest(TestCase):
    def test_ate_4_nivelcampo_order(self):

        teste = {
            'columns[2][data]': 'name',
            'columns[2][search][value]': 'ABADIA D',
            'columns[2][search][regex]': 'false',
            'columns[3][data]': 'uf',
            'columns[3][search][value]': 'MG',
        }

        result = {
            'columns': {
                '2': {
                    'data': 'name',
                    'search': {
                        'regex': 'false',
                        'value': 'ABADIA D'
                    }
                },
                '3': {
                    'data': 'uf',
                    'search': {
                        'value': 'MG'
                    }
                },
            }
        }
        self.assertTrue(qs_to_dict(teste) == result)