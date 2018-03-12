"""
    Formulario responsavel pela manipulação de objetos do tipo Option a
    nivel de dominio, ou seja aplicando apenas as regras de dominio.
"""

from django import forms
from survey.models import Option
from django.utils.text import slugify


class OptionModelForm(forms.ModelForm):
    """
        Implementação do formulario.
    """

    class Meta:
        """ Meta """
        model = Option
        fields = '__all__'

    def clean_name(self):

        name = self.cleaned_data.get('name')
        question = self.cleaned_data.get('question')

        original_slug = slugify(name)

        exists = True

        slug = original_slug
        counter = 1

        while exists:

            query_set = Option.objects.filter(name=slug, question=question)

            exists = query_set.exists()

            if exists:
                slug = original_slug + '-' + str(counter)
                counter += 1

        return slug

    def clean_question(self):

        question = self.cleaned_data.get('question')

        if not question.accepts_options:
            raise forms.ValidationError('Pergunta não permite opções')

        return question

