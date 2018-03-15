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
        exclude = (
            'question',
            'author',
        )

    def __init__(self, question, author, instance=None, **kwargs):

        self.question = question
        self.author = author
        kwargs.update({'question': question})
        kwargs.update({'author': author})

        if not instance:
            instance = self._retrieve_author_answer()
            kwargs.update({'author': author})

        super().__init__(instance=instance, **kwargs)

    def clean(self):
        cleaned_data = super().clean()

        # Regra de negocio:
        #   Autor e pergunta devem ser do mesmo questionario.
        if self.author.survey != self.question.survey:
            raise forms.ValidationError({
                '__all__': 'A pergunta e o autor não pertencem ao mesmo '
                           'questionário.'
            })

        # Edição de resposta
        if self.instance.pk:
            same_question = \
                self.instance.question.pk == self.question.pk

            if not same_question:
                raise forms.ValidationError({
                    '__all__': 'Esta resposta não pertence a esta pergunta'
                })

            same_author = \
                self.instance.author.pk == self.author.pk

            if not same_author:
                raise forms.ValidationError({
                    '__all__': 'Esta resposta não pertence a este autor'
                })

        return cleaned_data

    def save(self, commit=True):
        self.instance.question = self.question
        self.instance.author = self.author
        return super().save(commit=commit)

    def _retrieve_author_answer(self):
        """
        Verifica se usuário já respondeu o survey e, se sim, resgata
        a instância do formulário para seta-lo como edit.
        """
        try:
            return Answer.objects.get(question=self.question,
                                      author=self.author)
        except Answer.DoesNotExist:
            pass

        return None
