from abc import ABC, abstractmethod
from django.core.exceptions import ImproperlyConfigured

from base.exceptions import FormStepMissingBootstrapMappingError, \
    FormStepCannotBootstrapMissingDependency


class Step(object):
    # Class attributes
    template_name = None
    validated_antecessor_form = None
    dirty_antecessor_data = None
    form_class = None
    redirect_url = None

    post_data_dict = {}
    dependency_artifacts = {}

    # Internal bootstrapping stuff
    _dependes_on = ()
    _dependency_bootstrap_map = {}

    def __init__(self, validated_antecessor_form=None,
                 dirty_antecessor_data=None, **kwargs):

        if self.template_name is None and self.redirect_url is None:
            raise ImproperlyConfigured(
                "Step requires either a definition of 'template_name' "
                "'redirect_url'. ")

        if self.form_class is None:
            raise ImproperlyConfigured(
                "Step requires either a definition of 'form_class'")

        if validated_antecessor_form:
            self.validated_antecessor_form = validated_antecessor_form

        if dirty_antecessor_data:
            self.dirty_antecessor_data = dirty_antecessor_data

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

                if not self.dirty_antecessor_data and not \
                        self.validated_antecessor_form:
                    message = 'Validated antecessor form or antecessor ' \
                              'data required for bootstrapping the {} ' \
                              'dependency in the {} step.' \
                              ''.format(dependency,
                                        self.__class__.__name__)
                    raise FormStepCannotBootstrapMissingDependency(message)

                bootstrapper = self._dependency_bootstrap_map[dependency]

                new_artifact = bootstrapper.retrieve_artifact(
                    validated_antecessor_form=self.validated_antecessor_form,
                    dirty_antecessor_data=self.dirty_antecessor_data, **kwargs)

                if not new_artifact:
                    message = "Bootstrapper did not return a missing {} " \
                              "dependency artifact.".format(dependency)
                    raise FormStepCannotBootstrapMissingDependency(message)

                self.dependency_artifacts.update({dependency: new_artifact})


class StepBootstrapper(ABC):

    @abstractmethod
    def retrieve_artifact(self, validated_antecessor_form,
                          dirty_antecessor_data):
        pass
