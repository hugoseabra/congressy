"""
Manager é a definição centralizada de manipulação de um Model. Ou seja,
a intenção é que ele seja um serviço de domínio (Domain Service) responsável
por:
- Salvar model com suas devidas validações (premissas e restrições);
- Exigir a preexistência de objetos de dependência;
"""

from django import forms
from django.db.models import ObjectDoesNotExist

from survey.models import Survey


class Manager(forms.ModelForm):
    """
    Manager
    """
    pass
