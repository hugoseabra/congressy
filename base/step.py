from abc import ABC, abstractmethod
from django.core.exceptions import ImproperlyConfigured

from base.exceptions import FormStepMissingBootstrapMappingError, \
    FormStepCannotBootstrapMissingDependency


class Step(object):
    # Class attributes
    template_name = None
    antecessor_form = None
    form_class = None

    post_data_dict = {}
    dependency_artifacts = {}

    # Internal bootstrapping stuff
    _dependes_on = ()
    _dependency_bootstrap_map = {}

    def __init__(self, antecessor_form=None, **kwargs):

        if self.template_name is None:
            raise ImproperlyConfigured(
                "Step requires either a definition of 'template_name'")

        if self.form_class is None:
            raise ImproperlyConfigured(
                "Step requires either a definition of 'form_class'")
        if antecessor_form:
            self.antecessor_form = antecessor_form

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

                if not self.antecessor_form:
                    message = 'Missing antecessor form required for ' \
                           'bootstrapping the missing {} ' \
                           'dependency in the {} ' \
                           'step.'.format(dependency, self.__class__.__name__)
                    raise FormStepCannotBootstrapMissingDependency(message)

                bootstrapper = self._dependency_bootstrap_map[dependency]

                new_artifact = bootstrapper.retrieve_artifact(
                    antecessor_form=self.antecessor_form, **kwargs)

                if not new_artifact:
                    message = "{} did not return a dependency artifact " \
                              "".format(bootstrapper.__class__.__name__)
                    raise FormStepCannotBootstrapMissingDependency(message)

                self.dependency_artifacts.update({dependency: new_artifact})

    def get_next_step(self, **kwargs):
        raise ImproperlyConfigured(
            "Step requires an override of 'get_next_step' method to use "
            "it.")


class StepBootstrapper(ABC):

    @abstractmethod
    def retrieve_artifact(self, antecessor_form, **kwargs):
        pass
