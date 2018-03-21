"""
    Formulario responsavel pela manipulação de objetos do tipo Question a
    nivel de dominio, ou seja aplicando apenas as regras de dominio.
"""

from django import forms
from survey.models import Question
from django.utils.text import slugify


class QuestionModelForm(forms.ModelForm):
    """
        Implementação do formulario.
    """

    class Meta:
        """ Meta """
        model = Question
        fields = '__all__'

    def clean_name(self):

        name = self.cleaned_data.get('name')
        survey = self.cleaned_data.get('survey')

        original_slug = slugify(name)

        exists = True

        slug = original_slug
        counter = 1

        while exists:

            query_set = Question.objects.filter(name=slug, survey=survey)

            exists = query_set.exists()

            if exists:
                slug = original_slug + '-' + str(counter)
                counter += 1

        return slug


class QuestionForm(forms.Form):
    title = forms.CharField(
        label='Título',
        required=True,
        widget=forms.TextInput()
    )

    help_text = forms.CharField(
        label='Texto de ajuda',
        required=True,
        widget=forms.TextInput(),
        help_text='Uma instrução similar a está para ajudar seu participante '
                  'a entender melhor a pergunta.',
    )

    options = forms.CharField(
        label='Opções',
        required=False,
        widget=forms.Textarea(),
        help_text='Insira as opções da sua pergunta uma linha de cada vez.'
    )

