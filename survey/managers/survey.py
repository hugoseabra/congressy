"""
Manager é a definição centralizada de manipulação de um Model. Ou seja,
a intenção é que ele seja um serviço de domínio (Domain Service) responsável
por:
- Salvar model com suas devidas validações (premissas e restrições);
- Exigir a preexistência de objetos de dependência;
"""

from django import forms
from django.db.models import ObjectDoesNotExist

from .mixins import Manager
from survey.models import Survey


class SurveyManager(Manager):
    """
    Manager
    """
    class Meta:
        """ Meta """
        model = Survey
        fields = '__all__'

