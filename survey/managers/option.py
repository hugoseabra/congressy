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
        fields = '__all__'

    def clean_question(self):
        question = self.cleaned_data.get('question')

        if not question.accepts_options:
            raise forms.ValidationError('Pergunta não permite opções')

        return question

    def clean_name(self):
        """
        Slugify deve garantir que o nome de Question em um survey seja único.
        """
        name = self.cleaned_data.get('name')
        question = self.cleaned_data.get('question')

        original_slug = slugify(name)
        exists = True

        slug = original_slug
        counter = 1

        while exists:
            query_set = Option.objects.filter(
                name=slug,
                question=question
            )
            exists = query_set.exists()
            if exists:
                slug = original_slug + '-' + str(counter)
                counter += 1

        return slug
