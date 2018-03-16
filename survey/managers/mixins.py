"""
Manager é a definição centralizada de manipulação de um Model. Ou seja,
a intenção é que ele seja um serviço de domínio (Domain Service) responsável
por:
- Salvar model com suas devidas validações (premissas e restrições);
- Exigir a preexistência de objetos de dependência;
"""

from django import forms
from django.db.utils import IntegrityError
from django.forms.utils import ErrorList

from survey.models.mixins import Entity


class EntityTypeError(TypeError):
    """
    Exceção quando uma instância de entidade de domínio não pertence a
    superclasse Entity.
    """

    def __init__(self, message):
        self.message = 'Entidade não é instância de Entity: {}'.format(message)


class Manager(forms.ModelForm):
    """
    Manager
    """

    def __init__(self, **kwargs):
        data = kwargs.get('data')
        files = kwargs.get('files')
        auto_id = kwargs.get('auto_id', 'id_%s')
        prefix = kwargs.get('prefix')
        initial = kwargs.get('initial')
        instance = kwargs.get('instance')
        error_class = kwargs.get('error_class', ErrorList)
        label_suffix = kwargs.get('label_suffix')
        empty_permitted = kwargs.get('empty_permitted', False)
        use_required_attribute = kwargs.get('use_required_attribute')

        model = self.Meta.model
        if not issubclass(model, Entity):
            raise EntityTypeError(model)

        super().__init__(data=data, files=files, auto_id=auto_id,
                         prefix=prefix,
                         initial=initial, error_class=error_class,
                         label_suffix=label_suffix,
                         empty_permitted=empty_permitted, instance=instance,
                         use_required_attribute=use_required_attribute)

    def clean(self):
        try:
            cleaned_data = super().clean()

        except IntegrityError as e:
            msg = 'Erro de integridade: {}'.format(str(e))
            raise forms.ValidationError({'__all__': msg})

        return cleaned_data
