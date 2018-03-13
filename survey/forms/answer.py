"""
    Formulario responsavel pela manipulação de objetos do tipo Answer em
    nivel de dominio, ou seja, aplicando apenas as regras de dominio.
"""

from django import forms
from django.contrib.auth.models import User

from survey.models import Answer, Question


class AnswerModelForm(forms.ModelForm):
    """
        Implementação do formulario.
    """

    class Meta:
        """ Meta """
        model = Answer
        fields = '__all__'

    def __init__(self, user=None, instance=None, **kwargs):

        if not instance and isinstance(user, User):
            instance = self._retrieve_user_answer(user, kwargs.get('data'))

        super().__init__(instance=instance, **kwargs)

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
                return Answer.objects.get(
                    question=question,
                    user=user
                )

        except (Answer.DoesNotExist, Question.DoesNotExist):
            pass

        return None
