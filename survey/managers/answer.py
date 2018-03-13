"""
Manager é a definição centralizada de manipulação de um Model. Ou seja,
a intenção é que ele seja um serviço de domínio (Domain Service) responsável
por:
- Salvar model com suas devidas validações (premissas e restrições);
- Exigir a preexistência de objetos de dependência;
"""

from django import forms
from django.contrib.auth.models import User
from survey.models import Answer, Question


class AnswerManager(forms.ModelForm):
    """
        Implementação do formulario.
    """

    class Meta:
        """ Meta """
        model = Answer
        exclude = (
            'question',
            'user',
        )

    def __init__(self, question, user=None, instance=None, **kwargs):

        self.question = question
        self.user = user

        if not instance and isinstance(user, User):
            instance = self._retrieve_user_answer(user, kwargs.get('data'))

        super().__init__(instance=instance, **kwargs)

    def save(self, commit=True):
        self.instance.question = self.question
        self.instance.user = self.user
        return super().save(commit=commit)

    @staticmethod
    def _retrieve_user_answer(user, data):
        """
        Verifica se usuário já respondeu o survey e, se sim, resgata
        a instância do formulário para seta-lo como edit.
        """
        try:
            question_pk = data.get('question')

            if question_pk:
                question = Question.objects.get(pk=question_pk)
                return Answer.objects.get(question=question, user=user)

        except (Answer.DoesNotExist, Question.DoesNotExist):
            pass

        return None
