"""
Manager é a definição centralizada de manipulação de um Model. Ou seja,
a intenção é que ele seja um serviço de domínio (Domain Service) responsável
por:
- Salvar model com suas devidas validações (premissas e restrições);
- Exigir a preexistência de objetos de dependência;
"""

from django import forms

from survey.managers import Manager
from survey.models import Answer


class AnswerManager(Manager):
    """
        Manager
    """

    class Meta:
        """ Meta """
        model = Answer
        fields = '__all__'

    def __init__(self, **kwargs):

        data = kwargs.get('data')
        existing_instance = kwargs.get('instance')

        if not existing_instance:
            kwargs['instance'] = self._retrieve_author_answer(
                data.get('question'),
                data.get('author')
            )

        super().__init__(**kwargs)

    def clean_question(self):
        question = self.cleaned_data.get('question')

        # em caso de edição
        if self.instance.pk:

            if self.instance.question.pk != question.pk:
                raise forms.ValidationError(
                    'A resposta informada não pertence a esta pergunta.'
                )

        return question

    def clean_author(self):
        # Aplicação das Regras de negocio:
        # Condições para que regras sejam aplicadas:
        #   - Deve ser uma edição de uma respostas
        #
        # Regras:
        #
        #   - Author passado via instancia e autor passado via dados devem
        #       ser do mesmo questionario.
        #
        #   - Author passado via instancia e autor passado via dados devem
        #       possuir a mesma pergunta.

        # Resgatando os valores do campos de data.
        # Obs.: São instancias, e não apenas referencia: 'pk'
        author = self.cleaned_data.get('author')
        question = self.cleaned_data.get('question')

        # Deve ser uma edição de uma respostas
        if self.instance.pk:

            if self.instance.author.survey != author.survey:
                raise forms.ValidationError(
                    'A pergunta e o autor não pertencem ao mesmo questionário.'
                )

            if self.instance.question != question:
                raise forms.ValidationError(
                    'A resposta não pertence a este autor')

        return author

    @staticmethod
    def _retrieve_author_answer(question, author):
        """
        Verifica se usuário já respondeu o survey e, se sim, resgata
        a instância do formulário para seta-lo como edit.
        """
        try:
            return Answer.objects.get(question_id=question, author_id=author)

        except Answer.DoesNotExist:
            pass

        return None
