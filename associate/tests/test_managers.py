""" Testes de managers do módulo de Afiliados. """

from associate import managers
from base.tests.test_suites import ManagerPersistenceTestCase
from .mock_factory import MockFactory


class AssociateManagerPersistenceTest(ManagerPersistenceTestCase):
    """ Testes de persistência de dados: criação e edição."""
    manager_class = managers.AssociateManager
    required_fields = ('organization', 'name', 'email',)
    data_edit_to = {
        'name': 'another name edited',
    }

    def setUp(self):
        mock_factory = MockFactory()
        organization = mock_factory.create_fake_organization()

        self.data = {
            'name': 'my name',
            'email': 'myemail@me.com',
            'organization': organization.pk
        }

    def test_create(self):
        self.create()

    def test_edit(self):
        self.edit()
