"""
Define uma implementação de um Serviço de Aplicação (Application
Service) que rege uma pre-arquitetura de como estabelecer a comunicação
da aplicação com o domínio através de conectores diretos com Serviços de Domínio.
"""

from django import forms

from survey.managers.mixins import Manager
from django.forms.utils import ErrorList


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

    def __init__(self, **kwargs):

        data = kwargs.get('data')
        files = kwargs.get('files')
        auto_id = kwargs.get('auto_id', 'id_%s')
        prefix = kwargs.get('prefix')
        initial = kwargs.get('initial')
        error_class = kwargs.get('error_class', ErrorList)
        label_suffix = kwargs.get('label_suffix')
        empty_permitted = kwargs.get('empty_permitted', False)
        field_order = kwargs.get('field_order')
        use_required_attribute = kwargs.get('use_required_attribute')
        renderer = kwargs.get('renderer')

        super().__init__(data=data, files=files, auto_id=auto_id,
                         prefix=prefix, initial=initial,
                         error_class=error_class, label_suffix=label_suffix,
                         empty_permitted=empty_permitted,
                         field_order=field_order,
                         use_required_attribute=use_required_attribute,
                         renderer=renderer)

        self.manager = self._get_manager(**kwargs)

        # Injeta campos do manage (diretamente comunicando com Model) no
        # form de aplicação de serviço.

        self.fields.update(self.manager.fields)
        self.initial.update(self.manager.initial)

    @property
    def instance(self):
        return getattr(self.manager, 'instance')

    def _get_manager(self, **kwargs):
        manager_class = self._get_manager_class()

        manager = manager_class(**self._get_manager_kwargs(**kwargs))

        if not isinstance(manager, Manager):
            raise ManagerWrongTypeError('Manager inválido')

        return manager

    def _get_manager_class(self):
        if not self.manager_class:
            raise ManagerClassMissingError(
                "Você deve informar uma class de Manager do Model"
            )

        return self.manager_class

    def is_valid(self):
        manager_valid = self.manager.is_valid()
        if not manager_valid:
            self.errors.update(self.manager.errors)

        application_valid = super().is_valid()

        return application_valid is True and manager_valid is True

    def clean(self):
        cleaned_data = super().clean()
        if hasattr(self.manager_class, 'cleaned_data'):
            self.manager.cleaned_data.update(cleaned_data)
        cleaned_data.update(self.manager.cleaned_data)
        return cleaned_data

    def save(self, commit=True):
        return self.manager.save(commit=commit)

    def _get_manager_kwargs(self, **kwargs):
        return kwargs
