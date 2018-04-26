"""
    Testing the base Step
"""

from django.test.client import RequestFactory
from test_plus.test import TestCase
from base.step import StepView

# from base.form_step import Step, StepBootstrapper
# from base.exceptions import FormStepMissingBootstrapMappingError



class StepViewTest(TestCase):

    def setUp(self):
        # Every test needs access to the request factory.
        self.factory = RequestFactory()


    def test_step_GET_requests(self):

        request = self.factory = RequestFactory()





#
# class DependencyArtifact(object):
#     answer_attribute = 42
#
#
# class DependencyArtifactBootstrapper(StepBootstrapper):
#     fallback_step = 'do i need this?'
#     artifact_type = DependencyArtifact
#
#     def retrieve_artifact(self, **kwargs):
#         return DependencyArtifact()
#
#
# class NotABootstrapper(object):
#     pass
#
#
# class StepTest(TestCase):
#     """ Main test implementation """
#
#     def setUp(self):
#         self.bootstrapper = DependencyArtifactBootstrapper()
#         self.request_factory = RequestFactory()
#
#     def test_step_init_with_dependencies_and_no_bootstrapper(self):
#         """
#             Tests what happens when we create a step with a object dependency
#             and don't add a bootstrapper mapping.
#         """
#
#         class TestStepWithNoBoostrapper(Step):
#             dependes_on = ('DependencyArtifact',)
#
#         with self.assertRaises(FormStepMissingBootstrapMappingError):
#             TestStepWithNoBoostrapper(
#                 request=self.request_factory.get('/batman'))
#
#     def test_step_init_with_dependencies_and_wrong_bootstrapper_type(self):
#         """
#             Tests what happens when we create a step with a object dependency
#             and add a bootstrapper mapping that is not a StepBootstapper
#             subclass.
#         """
#
#         class TestStepWithWrongBootstraper(Step):
#             dependes_on = ('DependencyArtifact',)
#             dependency_bootstrap_map = {'DependencyArtifact': NotABootstrapper}
#
#         with self.assertRaises(TypeError):
#             TestStepWithWrongBootstraper(
#                 request=self.request_factory.get('/batman'))
#
#     def test_step_correct_bootstrapper_and_no_existing_artifacts(self):
#         class TestStepWithCorrectBootstrapper(Step):
#             dependes_on = ('DependencyArtifact',)
#
#             dependency_bootstrap_map = {
#                 'DependencyArtifact': DependencyArtifactBootstrapper}
#
#         step_instance = TestStepWithCorrectBootstrapper(
#             request=self.request_factory.get('/batman'))
#
#         artifact = step_instance.dependency_artifacts['DependencyArtifact']
#         self.assertIsInstance(artifact, DependencyArtifact)
#         self.assertIs(artifact.answer_attribute, 42)
#
#     def test_step_correct_bootstrapper_and_existing_artifacts(self):
#         class TestStepWithCorrectBootstrapper(Step):
#             dependes_on = ('DependencyArtifact',)
#
#             dependency_bootstrap_map = {
#                 'DependencyArtifact': DependencyArtifactBootstrapper}
#
#         existing_artifact = DependencyArtifact()
#         existing_artifact.answer_attribute = 43
#
#         step_instance = TestStepWithCorrectBootstrapper(
#             request=self.request_factory.get('/batman'),
#             dependency_artifacts={'DependencyArtifact': existing_artifact}
#         )
#
#         artifact = step_instance.dependency_artifacts['DependencyArtifact']
#         self.assertIsInstance(artifact, DependencyArtifact)
#         self.assertIs(artifact.answer_attribute, 43)




