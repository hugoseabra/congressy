"""
Manager é a definição centralizada de manipulação de um Model. Ou seja,
a intenção é que ele seja um serviço de domínio (Domain Service) responsável
por:
- Salvar model com suas devidas validações (premissas e restrições);
- Exigir a preexistência de objetos de dependência;
"""

from django import forms
from survey.models import Option
from django.utils.text import slugify


class OptionManager(forms.ModelForm):
    """ Manager """

    class Meta:
        """ Meta """
        model = Option
        exclude = (
            'question',
        )

    def __init__(self, question, *args, **kwargs):
        self.question = question
        super().__init__(*args, **kwargs)

    def clean_name(self):
        """
        Slugify deve garantir que o nome de Question em um survey seja único.
        """
        name = self.cleaned_data.get('name')

        original_slug = slugify(name)
        exists = True

        slug = original_slug
        counter = 1

        while exists:
            query_set = Option.objects.filter(name=slug, question=self.question)
            exists = query_set.exists()
            if exists:
                slug = original_slug + '-' + str(counter)
                counter += 1

        return slug

    def clean(self):
        cleaned_data = super().clean()

        if not self.question.accepts_options:
            raise forms.ValidationError(
                {'questionz': 'Pergunta não permite opções'}
            )

        return cleaned_data

    def save(self, commit=True):
        self.instance.question = self.question
        return super().save(commit=commit)
