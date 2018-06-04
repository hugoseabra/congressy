"""
Manager é a definição centralizada de manipulação de um Model. Ou seja,
a intenção é que ele seja um serviço de domínio (Domain Service) responsável
por:
- Salvar model com suas devidas validações (premissas e restrições);
- Exigir a preexistência de objetos de dependência;
"""

from django import forms

from base.models import EntityMixin

__all__ = ['ManagerException', 'EntityTypeError', 'Manager']


class ManagerException(TypeError):
    """
    Exceção quando o manager processo algo inesperado.
    """


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
        model = self.Meta.model
        if not issubclass(model, EntityMixin):
            raise EntityTypeError(model)

        super().__init__(**kwargs)

    def hide_field(self, field_name):
        if field_name not in self.fields:
            raise ManagerException('O campo "{}" não existe em "{}"'.format(
                field_name,
                self.__class__
            ))

        self.fields[field_name].widget = forms.HiddenInput()

    def get(self, pk):
        return self.Meta.model.objects.get(pk=pk)
