"""
Manager é a definição centralizada de manipulação de um Model. Ou seja,
a intenção é que ele seja um serviço de domínio (Domain Service) responsável
por:
- Salvar model com suas devidas validações (premissas e restrições);
- Exigir a preexistência de objetos de dependência;
"""

from survey.models import Survey
from .mixins import Manager


class SurveyManager(Manager):
    """
    Manager
    """

    class Meta:
        """ Meta """
        model = Survey
        fields = '__all__'
