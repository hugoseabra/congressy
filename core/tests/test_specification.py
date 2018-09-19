from test_plus.test import TestCase

from core.specification import CompositeSpecification


class User(object):

    def __init__(self, super_user=False):
        self.super_user = super_user


class UserSpecification(CompositeSpecification):

    def is_satisfied_by(self, candidate):
        return isinstance(candidate, User)


class SuperUserSpecification(CompositeSpecification):

    def is_satisfied_by(self, candidate):
        return getattr(candidate, 'super_user', False)


class SpecificationTest(TestCase):

    def setUp(self):
        self.andrey = User()
        self.ivan = User(super_user=True)
        self.vasiliy = 'not User instance'

    def test_single_spec(self):
        root_specification = UserSpecification()
        self.assertTrue(root_specification.is_satisfied_by(self.andrey))
        self.assertTrue(root_specification.is_satisfied_by(self.ivan))
        self.assertFalse(root_specification.is_satisfied_by(self.vasiliy))

    def test_combined_and_spec(self):
        root_specification = UserSpecification(). \
            and_specification(SuperUserSpecification())

        self.assertFalse(root_specification.is_satisfied_by(self.andrey))
        self.assertTrue(root_specification.is_satisfied_by(self.ivan))
        self.assertFalse(root_specification.is_satisfied_by(self.vasiliy))

    def test_combined_or_spec(self):
        root_specification = UserSpecification(). \
            or_specification(SuperUserSpecification())

        self.assertTrue(root_specification.is_satisfied_by(self.andrey))
        self.assertTrue(root_specification.is_satisfied_by(self.ivan))
        self.assertFalse(root_specification.is_satisfied_by(self.vasiliy))

    def test_combined_not_spec(self):
        root_specification = UserSpecification().not_specification()

        self.assertFalse(root_specification.is_satisfied_by(self.andrey))
        self.assertFalse(root_specification.is_satisfied_by(self.ivan))
        self.assertTrue(root_specification.is_satisfied_by(self.vasiliy))
