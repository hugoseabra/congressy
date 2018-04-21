""" Testes de managers do módulo de Afiliados. """

from associate import services
from base.tests.test_suites import ApplicationServicePersistenceTestCase
from .mock_factory import MockFactory


class AssociateServicePersistenceTest(ApplicationServicePersistenceTestCase):
    """ Testes de persistência de dados: criação e edição."""
    application_service_class = services.AssociateService
    required_fields = ('organization', 'name', 'email',)
    data_edit_to = {
        'name': 'another name edited',
    }

    def setUp(self):
        mock_factory = MockFactory()
        organization = mock_factory.create_fake_organization()

        self.data = {
            'name': 'my name',
            'email': 'myemal@me.com',
            'organization': organization.pk,
        }

    def test_create(self):
        self.create()

    def test_edit(self):
        self.edit()
