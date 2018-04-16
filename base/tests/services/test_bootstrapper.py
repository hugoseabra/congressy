"""
    Test for the base StepBootstraper
"""

from test_plus.test import TestCase
from base.step import StepBootstrapper


class StepBootstrapperTest(TestCase):

    def test_bootstrapper_init_with_missing_methods(self):
        """
            Tests if the bootstrap subclassing init follows our basic design
            goals when we leave out certain a methods.
        """

        class BootstrapperSubclass(StepBootstrapper):
            pass

        with self.assertRaises(TypeError):
            BootstrapperSubclass()

    def test_bootstrapper_init_with_missing_attributes(self):
        """
            Tests if the bootstrap subclassing init follows our basic design
            goals when we leave out certain attributes.
        """

        class BootstrapperSubclass(StepBootstrapper):

            def retrieve_artifact(self, **kwargs):
                pass

        with self.assertRaises(NotImplementedError):
            BootstrapperSubclass()
