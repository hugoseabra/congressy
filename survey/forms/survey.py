from django import forms
from django.forms import ValidationError
from django.forms.fields import Field as DjangoField

from survey.models import Survey, Question, Author, Answer
from survey.services import AnswerService
from .field import SurveyField


class SurveyForm(forms.Form):
    """ Formulário Dinâmico. """

    def __init__(self, survey, user=None, *args, **kwargs):

        if not isinstance(survey, Survey):
            msg = '{} não é uma instância de Survey'.format(
                survey.__class__.__name__)
            raise ValueError(msg)

        self.survey = survey
        self.user = user
        super(SurveyForm, self).__init__(*args, **kwargs)

        if self.survey.questions:

            for question in self.survey.questions.all().order_by('order'):
                self.create_field(name=question.name,
                                  field_type=question.type,
                                  label=question.label,
                                  required=question.required,
                                  help_text=question.help_text,
                                  intro=question.intro,
                                  question=question)

    def create_field(self, question, name, field_type, initial=None,
                     required=False, help_text=None, intro=False,
                     label=None, **kwargs):
        """
        Cria um campo para o formulário conforme interface django field:
        field e widget.
        :param question: uma instância das perguntas.
        :param help_text: o texto de ajuda
        :param intro: se o primeiro campo será vazio
        :param label: um titulo para pergunta
        :param name: Nome do campo
        :param field_type: tipo do campo, conforme survey.fields.Field
        :param initial: valor inicial
        :param required: se obrigatório
        :param label: valor do rótulo
        :param kwargs: outros valores
        :rtype: DjangoField
        """

        field = SurveyField(question, field_type, initial, required, label,
                            help_text=help_text, select_intro=intro, **kwargs)
        self.fields[name] = field.get_django_field()

    def save_answers(self) -> list:
        """

        :return: list: uma lista de objetos do tipo Answer que corresponde a
                        todas as respostas das perguntas deste formulario.

        :raises ValidationError: exception sobe caso o serviço de resposta
        não consiga validar corretamente.
        """

        answer_list = []

        for question, answer in self.cleaned_data.items():

            if answer:

                author = Author.objects.get_or_create(survey=self.survey,
                                                      user=self.user)[0]

                question = Question.objects.get(name=question,
                                                survey=self.survey)

                existing_answer = None

                try:
                    existing_answer = Answer.objects.get(question=question.pk,
                                                         author=author)
                except Answer.DoesNotExist:
                    pass

                if existing_answer:
                    answer_service = AnswerService(instance=existing_answer,
                                                   data={
                                                       'question': question.pk,
                                                       'author': author.pk,
                                                       'value': answer,
                                                   })
                else:
                    answer_service = AnswerService(data={
                        'question': question.pk,
                        'author': author.pk,
                        'value': answer,
                    })

                if answer_service.is_valid():
                    answer_object = answer_service.save()
                    answer_list.append(answer_object)
                else:
                    msg = 'Não foi possivel validar a resposta: {}'.format(
                        answer_service.data)
                    raise ValidationError(msg)

        return answer_list
