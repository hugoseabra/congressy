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

        model = self.Meta.model
        if not issubclass(model, Entity):
            raise EntityTypeError(model)

        super().__init__(**kwargs)

    def get(self, pk):
        return self.Meta.model.objects.get(pk=pk)
