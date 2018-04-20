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


