"""
Define uma implementação de um Serviço de Aplicação (Application
Service) que rege uma pre-arquitetura de como estabelecer a comunicação
da aplicação com o domínio através de conectores diretos com Serviços de Domínio.
"""

from django import forms


from survey.managers.mixins import Manager


class ManagerClassMissingError(Exception):
    """ Classe de Manager não existe no Application Service. """
    pass


class ManagerWrongTypeError(Exception):
    """
    Classe de Manager não é uma instância de 'survey.managers.mixins.Manager'.
    """
    pass


class ApplicationServiceMixin(forms.Form):
    """
    Application Service
    """
    manager_class = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.manager = self._get_manager(**kwargs)

        # Injeta campos do manage (diretamente comunicando com Model) no
        # form de aplicação de serviço.

        self.fields.update(self.manager.fields)
        self.initial.update(self.manager.initial)

    def _get_manager(self, **kwargs):
        manager_class = self._get_manager_class()
        manager = manager_class(self._get_manager_kwargs(**kwargs))

        if not isinstance(manager, Manager):
            raise ManagerWrongTypeError('Manager inválido.')

        return manager

    def _get_manager_class(self):
        if not self.manager_class:
            raise ManagerClassMissingError(
                "Você deve informar uma class de Manager do Model."
            )

        return self.manager_class

    def _get_manager_kwargs(self, **kwargs):
        return kwargs

    def is_valid(self):
        manager_valid = self.manager.is_valid()
        if not manager_valid:
            self.errors.update(self.manager.errors)

        application_valid = super().is_valid()

        return application_valid is True and manager_valid is True

    def clean(self):
        cleaned_data = super().clean()
        cleaned_data.update(self.manager.cleaned_data)
        return cleaned_data

    def save(self, commit=True):
        return self.manager.save(commit=commit)

    def get(self, pk):
        return self.manager.get(pk=pk)
