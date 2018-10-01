"""
Manager é a definição centralizada de manipulação de um Model. Ou seja,
a intenção é que ele seja um serviço de domínio (Domain Service) responsável
por:
- Salvar model com suas devidas validações (premissas e restrições);
- Exigir a preexistência de objetos de dependência;
"""

from django import forms
from django.utils.text import slugify

from survey.managers import Manager
from survey.models import Option


class OptionManager(Manager):
    """ Manager """

    class Meta:
        """ Meta """
        model = Option
        fields = ('question', 'name',)

    def clean_question(self):
        """
            Implementação da regra de negocio:

                - Deve sempre ser de uma pergunta que suporte opções:
                    SELECT, RADIO ou CHECKBOX;

        """

        question = self.cleaned_data.get('question')

        if not question.accepts_options:
            raise forms.ValidationError('Pergunta não permite opções')

        return question

    def save(self, commit=True):
        self.instance.value = self._create_slug()
        return super().save(commit)

    def _create_slug(self):
        """
            Slugify deve garantir que o nome de Option em uma Question seja
            único.
        """
        name = self.cleaned_data.get('name')
        question = self.cleaned_data.get('question')

        original_slug = slugify(name)

        slug = original_slug

        existing_options = Option.objects.filter(
            question=question,
            value=slug,
        )

        if existing_options.count() >= 1:
            counter = 1
            for option in existing_options:

                query_set = Option.objects.filter(
                    value=option.value,
                    question=question
                )

                if query_set.exists():
                    slug = original_slug + '-' + str(counter)
                    counter += 1

        return slug
