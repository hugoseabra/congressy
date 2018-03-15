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

        instance = kwargs.get('instance')

        # Em caso de edição
        if instance and instance.pk:
            data = kwargs.get('data')
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
        author = self.cleaned_data.get('author')
        question = self.cleaned_data.get('question')

        # em caso de edição
        if self.instance.pk and self.instance.author.pk != author.pk:
            raise forms.ValidationError('A resposta não pertence a este autor')

        # Regra de negocio:
        #   Autor e pergunta devem ser do mesmo questionario.
        if author.survey != question.survey:
            raise forms.ValidationError(
                'A pergunta e o autor não pertencem ao mesmo questionário.'
            )

        return author

    @staticmethod
    def _retrieve_author_answer(question, author):
        """
        Verifica se usuário já respondeu o survey e, se sim, resgata
        a instância do formulário para seta-lo como edit.
        """
        try:
            return Answer.objects.get(question=question, author=author)

        except Answer.DoesNotExist:
            pass

        return None
