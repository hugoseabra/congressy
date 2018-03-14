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

        if not instance:
            instance = self._retrieve_author_answer()

        super().__init__(instance=instance, **kwargs)

    def clean(self):
        cleaned_data = super().clean()

        if self.instance.pk:
            same_survey = \
                self.instance.question.survey.pk == self.question.survey.pk

            if not same_survey:
                raise forms.ValidationError({
                    '__all__': 'Esta resposta não pertence a este'
                               ' questionário.'
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
