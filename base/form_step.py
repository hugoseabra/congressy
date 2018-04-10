from abc import ABC, abstractmethod
from django.shortcuts import render

from base.exceptions import FormStepMissingBootstrapMappingError, \
    FormStepCannotBootstrapMissingDependency


class Step(object):
    dependes_on = ()
    dependency_bootstrap_map = {}
    request = None
    form_instance = None
    form_class = None
    template = None
    redirect_to = None
    context = {}

    dependency_artifacts = {}

    def __init__(self, request, form=None, context=None,
                 dependency_artifacts=None,
                 **kwargs) -> None:

        self.request = request

        if form:
            self.form_instance = form

        if dependency_artifacts:
            self.dependency_artifacts = dependency_artifacts

        if context:
            self.context = context

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

        super().__init__()

    def _validate_dependency_mappings(self):

        for dependency in self.dependes_on:

            if dependency not in self.dependency_bootstrap_map:
                message = "Missing {} dependency bootstrap mapping " \
                    .format(dependency)
                raise FormStepMissingBootstrapMappingError(message)

            if isinstance(self.dependency_bootstrap_map[dependency],
                          StepBootstrapper):
                message = "Dependency bootstrapper mapping {} is not an " \
                          "instance of StepBootstrapper" \
                          "".format(dependency)
                raise TypeError(message)

    def _bootstrap_missing_dependencies(self, **kwargs):

        for dependency in self.dependes_on:

            if dependency not in self.dependency_artifacts:

                bootstrapper = self.dependency_bootstrap_map[dependency]

                new_artifact = bootstrapper.reretrieve_artifact(kwargs)

                if not new_artifact:
                    message = "{} did not return a dependency artifact "
                    raise FormStepCannotBootstrapMissingDependency(message)

                self.dependency_artifacts.update({dependency: new_artifact})

    def get_context(self):

        return self.context

    def render(self):

        if not self.template:
            raise AttributeError('Step is missing a template')

        context = self.get_context()

        response = render(request=self.request, template_name=self.template,
                          context=context)

        return response


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
