"""
    Serviço de Aplicação para Perguntas

    Deve permitir as seguintes ações:

        1. Adicionar uma pergunta;
        2. Resgatar uma pergunta;
        3. Editar uma pergunta;
        4. Excluir uma pergunta;

"""
from survey.services import mixins
from survey.managers import QuestionManager


class QuestionService(mixins.ApplicationServiceMixin):
    """ Application Service """
    manager_class = QuestionManager

    """
        ### Novo Pergunta
    
        É possível criar uma Pergunta e depois adicionar ao Questionário:
        
        ```python
        question_service = QuestionService()
         
        question = question_service.create(
            type=constants.INPUT_TYPE,
            label='Qual o seu nome?',
            required=True,
            help_text='Informe o seu nome completo.'
        )
         
        
        survey.add_question(question)
    """