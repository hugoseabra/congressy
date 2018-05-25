"""
    Mock factory used during tests to create required objects
"""

from faker import Faker

from associate.models import Associate
from gatheros_event.models import Organization


class MockFactory:
    """
        Mock Factory Implementation
    """

    def __init__(self):
        self.fake_factory = Faker()

    def create_fake_associate(self):
        return Associate.objects.create(
            name=self.fake_factory.name(),
            organization=self.create_fake_organization()
        )

    def create_fake_organization(self):
        return Organization.objects.create(name=self.fake_factory.company())
