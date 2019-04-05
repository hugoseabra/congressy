from django.test import TestCase
from faker import Faker

from ticket.tests import MockFactory


class TicketAPITest(TestCase):

    def setUp(self) -> None:
        super().setUp()
        self.faker = Faker('pt_BR')
        self.mock_factory = MockFactory()

    def test_organizer_only_create(self):
        """
        As unicas pessoas que podem criar tickets são os organizadores do
        evento
        """

        self.fail("Not Implemented")

    def test_organizer_only_update(self):
        """
        As unicas pessoas que podem atualizar tickets são os organizadores do
        evento
        """

        self.fail("Not Implemented")

    def test_organizer_only_delete(self):
        """
        As unicas pessoas que podem atualizar tickets são os organizadores do
        evento
        """

        self.fail("Not Implemented")

    def test_delete(self):
        """
        Só é possível apagar um ticket caso não possua nenhuma
        inscrição
        """

        self.fail("Not Implemented")
