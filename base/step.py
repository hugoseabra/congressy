from abc import ABC, abstractmethod
from django.core.exceptions import ImproperlyConfigured
from django.views.generic import TemplateView

from base.exceptions import FormStepMissingBootstrapMappingError, \
    FormStepCannotBootstrapMissingDependency


class Step(object):

    # Class attributes
    template_name = None
    form_class = None
    post_data_dict = {}
    dependency_artifacts = {}

    # Internal bootstrapping stuff
    _dependes_on = ()
    _dependency_bootstrap_map = {}

    def __init__(self, *args, **kwargs):

        if self.template_name is None:
            raise ImproperlyConfigured(
                "Step requires either a definition of 'template_name'")

        if self.form_class is None:
            raise ImproperlyConfigured(
                "Step requires either a definition of 'form_class'")

        data_dict = kwargs.get('post_data_dict')
        dependency_artifacts = kwargs.get('dependency_artifacts')

        if data_dict:
            self.post_data_dict = data_dict

        if dependency_artifacts:
            self.dependency_artifacts = dependency_artifacts

        # Internal bootstraping-capability checking, does every step dependency
        # have a mapping, or in other words, a way to self bootstrap if it's
        # not supplied?

        if bool(self._dependes_on):
            self._validate_dependency_mappings()

            # Only try to bootstrap if any dependencies are missing
            for dependency in self._dependes_on:
                if dependency not in self.dependency_artifacts:
                    self._bootstrap_missing_dependencies(**kwargs)
                    break

        super().__init__()

    def _validate_dependency_mappings(self):

        for dependency in self._dependes_on:

            if dependency not in self._dependency_bootstrap_map:
                message = "Missing {} dependency bootstrap mapping " \
                    .format(dependency)
                raise FormStepMissingBootstrapMappingError(message)

            if not issubclass(self._dependency_bootstrap_map[dependency],
                              StepBootstrapper):
                message = "Dependency bootstrapper mapping {} is not an " \
                          "instance of StepBootstrapper" \
                          "".format(dependency)
                raise TypeError(message)

    def _bootstrap_missing_dependencies(self, **kwargs):

        for dependency in self._dependes_on:

            if dependency not in self.dependency_artifacts:

                bootstrapper = self._dependency_bootstrap_map[dependency]

                new_artifact = bootstrapper.retrieve_artifact(kwargs)

                if not new_artifact:
                    message = "{} did not return a dependency artifact "
                    raise FormStepCannotBootstrapMissingDependency(message)

                self.dependency_artifacts.update({dependency: new_artifact})

    def get_next_step(self, **kwargs):
            raise ImproperlyConfigured(
                "Step requires an override of 'get_next_step' method")







# class Step(object):
#     dependes_on = ()
#     dependency_bootstrap_map = {}
#     form_instance = None
#     form_class = None
#     template = None
#     redirect_to = None
#     fallback_step = None
#     context = {}
#
#     dependency_artifacts = {}
#
#     def __init__(self, form=None, context=None,
#                  dependency_artifacts=None,
#                  **kwargs) -> None:
#
#         if form:
#             self.form_instance = form
#
#         if dependency_artifacts:
#             self.dependency_artifacts = dependency_artifacts
#
#         if context:
#             self.context = context
#
#         # Internal bootstraping-capability checking, does every step dependency
#         # have a mapping, or in other words, a way to self bootstrap if it's
#         # not supplied?
#
#         if bool(self.dependes_on):
#             self._validate_dependency_mappings()
#
#             # Only try to bootstrap if any dependencies are missing
#             for dependency in self.dependes_on:
#                 if dependency not in self.dependency_artifacts:
#                     self._bootstrap_missing_dependencies(**kwargs)
#                     break
#
#         super().__init__()
#
#     def _validate_dependency_mappings(self):
#
#         for dependency in self.dependes_on:
#
#             if dependency not in self.dependency_bootstrap_map:
#                 message = "Missing {} dependency bootstrap mapping " \
#                     .format(dependency)
#                 raise FormStepMissingBootstrapMappingError(message)
#
#             if not issubclass(self.dependency_bootstrap_map[dependency],
#                               StepBootstrapper):
#                 message = "Dependency bootstrapper mapping {} is not an " \
#                           "instance of StepBootstrapper" \
#                           "".format(dependency)
#                 raise TypeError(message)
#
#     def _bootstrap_missing_dependencies(self, **kwargs):
#
#         for dependency in self.dependes_on:
#
#             if dependency not in self.dependency_artifacts:
#
#                 bootstrapper = self.dependency_bootstrap_map[dependency]
#
#                 new_artifact = bootstrapper.retrieve_artifact(kwargs)
#
#                 if not new_artifact:
#                     message = "{} did not return a dependency artifact "
#                     raise FormStepCannotBootstrapMissingDependency(message)
#
#                 self.dependency_artifacts.update({dependency: new_artifact})
#
#     def validate(self, **kwargs) -> bool:
#
#         if self.form_class:
#
#             if not self.form_instance:
#                 self.form_instance = self.form_class(kwargs)
#
#             return self.form_instance.is_valid()
#
#         return False
#
#     def get_form_instance(self):
#         return self.form_instance
#
#     def get_context(self):
#         return self.context
#
#
class StepBootstrapper(ABC):
    fallback_step = None
    artifact_type = None

    def __init__(self) -> None:

        super().__init__()

        if not self.fallback_step:
            raise NotImplementedError('StepBootstrapper must define a '
                                      'fallback_step')

        if not self.artifact_type:
            raise NotImplementedError('StepBootstrapper must define a '
                                      'artifact_type')

    @abstractmethod
    def retrieve_artifact(self, **kwargs):
        pass


class TemplateStep(TemplateView):

    dependes_on = ()
    dependency_bootstrap_map = {}
    dependency_artifacts = {}

    def __init__(self, context=None, form=None,
                 dependency_artifacts=None, *args,
                 **kwargs) -> None:

        if form:
            self.form_instance = form

        if dependency_artifacts:
            self.dependency_artifacts = dependency_artifacts

        if context:
            self.context = context

        super().__init__(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Internal bootstraping-capability checking, does every step dependency
        # have a mapping, or in other words, a way to self bootstrap if it's
        # not supplied?

        if bool(self.dependes_on):
            self._validate_dependency_mappings()

            # Only try to bootstrap if any dependencies are missing
            for dependency in self.dependes_on:
                if dependency not in self.dependency_artifacts:
                    self._bootstrap_missing_dependencies(**kwargs)
                    break

            for dependency, artifact in self.dependency_artifacts:
                context[dependency] = artifact

        return context

    def _validate_dependency_mappings(self):

        for dependency in self.dependes_on:

            if dependency not in self.dependency_bootstrap_map:
                message = "Missing {} dependency bootstrap mapping " \
                    .format(dependency)
                raise FormStepMissingBootstrapMappingError(message)

            if not issubclass(self.dependency_bootstrap_map[dependency],
                              StepBootstrapper):
                message = "Dependency bootstrapper mapping {} is not an " \
                          "instance of StepBootstrapper" \
                          "".format(dependency)
                raise TypeError(message)

    def _bootstrap_missing_dependencies(self, **kwargs):

        for dependency in self.dependes_on:

            if dependency not in self.dependency_artifacts:

                bootstrapper = self.dependency_bootstrap_map[dependency]

                new_artifact = bootstrapper.retrieve_artifact(kwargs)

                if not new_artifact:
                    message = "{} did not return a dependency artifact "
                    raise FormStepCannotBootstrapMissingDependency(message)

                self.dependency_artifacts.update({dependency: new_artifact})


