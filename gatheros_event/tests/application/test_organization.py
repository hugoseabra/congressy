from unittest import skip

from django.test import TestCase


class OrganizationModelTest(TestCase):
    @skip
    def test_internal_edition_not_allowed(self):
        pass
