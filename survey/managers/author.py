"""
Manager é a definição centralizada de manipulação de um Model. Ou seja,
a intenção é que ele seja um serviço de domínio (Domain Service) responsável
por:
- Salvar model com suas devidas validações (premissas e restrições);
- Exigir a preexistência de objetos de dependência;
"""

from django import forms
from django.contrib.auth.models import User

from survey.models import Author


class AuthorManager(forms.ModelForm):
    """ Manager """

    class Meta:
        """ Meta """
        model = Author
        exclude = (
            'survey',
            'user',
        )

    def __init__(self, survey, user=None, instance=None, **kwargs):
        self.survey = survey
        self.user = user

        if not instance and isinstance(user, User):
            instance = self._retrieve_user_author(survey, user)

        super().__init__(instance=instance, **kwargs)

    def clean(self):
        cleaned_data = super().clean()

        if self.instance:
            same_survey = \
                self.instance.survey.pk == self.survey.pk

            if not same_survey:
                raise forms.ValidationError({
                    '__all__': 'Este autor não pertence a este questionário.'
                })

        return cleaned_data

    def save(self, commit=True):
        self.instance.survey = self.question
        self.instance.user = self.user
        return super().save(commit=commit)

    @staticmethod
    def _retrieve_user_author(survey, user):
        """
        Verifica se usuário já possui referência como autor para o
        questionário.
        """
        if not isinstance(user, User):
            return None

        try:
            return Author.objects.get(user=user, survey=survey)

        except Author.DoesNotExist:
            pass

        return None
