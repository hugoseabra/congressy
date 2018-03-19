"""
    Serviço de Aplicação para Questionário

    Deve permitir as seguintes ações:

        1. Criar novo questionário;
        2. Resgatar questionário preexistente;
        3. Alterar questionário;
        4. Excluir questionário;

"""
from survey.services import mixins
from survey.managers import SurveyManager
from django.forms import ValidationError
from survey.models import Survey


class SurveyService(mixins.ApplicationServiceMixin):
    """ Implementação do Serviço de Aplicação de Questionários """
    manager_class = SurveyManager

    def create(self, name: str, description: str) -> Survey:
        """
        Criar um novo questionário.

        Utilização:
            ```python
            # Service é responsável para abstrair toda complexidade.
            service = SurveyService()

            # Objeto de questionário com suporte a todas as ações
            survey = service.create(
                name='Meu questionário',
                description='Formulário exemplo'
            )
            ```

        :param name: string
        :param description: string
        :return Survey: object
        """

        data = {
            'name': name,
            'description': description
        }

        self.manager.data = data
        self.manager.is_bound = True

        if not self.manager.is_valid():
            raise ValidationError(self.manager.errors)

        return self.manager.save()
