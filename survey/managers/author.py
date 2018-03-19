"""
Manager é a definição centralizada de manipulação de um Model. Ou seja,
a intenção é que ele seja um serviço de domínio (Domain Service) responsável
por:
- Salvar model com suas devidas validações (premissas e restrições);
- Exigir a preexistência de objetos de dependência;
"""

from django import forms
from django.contrib.auth.models import User

from survey.managers import Manager
from survey.models import Author


class AuthorManager(Manager):
    """ Manager """

    class Meta:
        """ Meta """
        model = Author
        fields = '__all__'

    def __init__(self, user=None, **kwargs):

        self.user = user

        if self.user and type(user) == int:
            try:
                self.user = User.objects.get(pk=user)
            except User.DoesNotExist:
                pass

        data = self._set_author_data_from_user(
            kwargs.get('data', {}),
        )
        kwargs['data'] = data

        kwargs['instance'] = self._set_instance_from_user(
            user,
            data.get('survey'),
            kwargs.get('instance')
        )

        super().__init__(**kwargs)

    def clean(self):
        cleaned_data = super().clean()

        if self.instance.pk:
            survey = self.cleaned_data.get('survey')

            if self.instance.survey.pk != survey.pk:
                raise forms.ValidationError({
                    '__all__': 'Este autor não pertence a este questionário.'
                })

        return cleaned_data

    def _set_author_data_from_user(self, data):
        """
        Se um usuário (não anônimo) for passado, preservar os dados de usuário
        nos dados de autor.
        """
        # Garante possibilidade de alteração da dict()
        data = data.copy()

        if isinstance(self.user, User) and not self.user.is_anonymous():

            # Nome do autor é o nome do usuário
            data['name'] = self.user.get_full_name()

            # User deve estar em data
            data.update({'user': self.user.pk})

        return data

    def _set_instance_from_user(self, user, survey_pk, instance):
        """
        Se user (não anônimo) for passado e não houver instância de Autor,
        resgata autor vinculado ao usuário da persistência (se existir).
        """
        # Se estiver tudo ok com a instância, ela deve ser retornada.
        if isinstance(instance, self.Meta.model):
            return instance

        # Não aceitar instância de usuários anômimo
        if not isinstance(user, User) or user.is_anonymous():
            return None

        return self._retrieve_user_author(survey_pk)

    def _retrieve_user_author(self, survey_pk):
        """
        Verifica se usuário já possui referência como autor para o
        questionário.
        """

        try:
            return Author.objects.get(user=self.user, survey_id=survey_pk)

        except Author.DoesNotExist:
            pass

        return None
