"""
    Base Exceptions
"""


class FormStepMissingBootstrapMappingError(Exception):
    """ Exceção acontece quando um step de formulario não possui um
    mapeamento de bootstrap """
    pass


class FormStepCannotBootstrapMissingDependency(Exception):
    """ Exceção acontece quando um step de formulario não consegui criar o
    um artefato de dependencia que estava faltado """
    pass


class InvalidFormWizardStep(Exception):
    """ Exceção acontece quando um step não pertence a um wizard"""
    pass


