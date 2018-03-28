"""
    Formulario responsavel pela manipulação de objetos do tipo Question a
    nivel de dominio, ou seja aplicando apenas as regras de dominio.
"""

from django import forms
from django.utils.text import slugify
from django.contrib import messages
from survey.models import Question
from survey.services import QuestionService, OptionService


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
    name = forms.CharField(
        label='Nome do campo',
        required=True,
        widget=forms.TextInput()
    )

    help_text = forms.CharField(
        label='Texto de ajuda',
        required=False,
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

    empty_intro = forms.BooleanField(
        label='Primeiro campo vazio',
        required=False,
        help_text='Deixar o primeiro item da lista em branco',
    )

    def __init__(self, survey, **kwargs):
        self.survey = survey
        super().__init__(**kwargs)
        self.service = QuestionService(**kwargs)

    def is_valid(self):
        form_is_valid = super().is_valid()
        service_is_valid = self.service.is_valid()
        return form_is_valid and service_is_valid

    def save(self):
        question = self.service.save()

        options = self.cleaned_data.get('options', None)

        if options:
            option_list = options.splitlines()
            for option in option_list:
                option_data = {
                    'question': question.pk,
                    'name': option,
                    'value': option
                }
                option_service = OptionService(data=option_data)
                if option_service.is_valid():
                    option_service.save()
                else:
                    messages.error(
                        self.request,
                        "Não foi possivel salvar a opção: {}".format(option)
                    )

        return question
