import os

from django import forms
from django.conf import settings
from django.db.transaction import atomic
from django.core.files.storage import FileSystemStorage
from django.forms import ValidationError
from django.forms.fields import Field as DjangoField

from core.model.validator import cpf_validator, cnpj_validator
from survey.models import Survey, Question, Author, Answer
from survey.services import AnswerService
from .field import SurveyField


class SurveyBaseForm(forms.Form):
    """ Formulário Dinâmico. """

    def __init__(self, survey, user=None, author=None, *args, **kwargs):

        if not isinstance(survey, Survey):
            msg = '{} não é uma instância de Survey'.format(
                survey.__class__.__name__
            )
            raise ValueError(msg)

        self.survey = survey
        self.user = user
        self.author = author

        self.storage = FileSystemStorage(
            location=os.path.join(settings.MEDIA_ROOT, 'survey', 'pdfs'),
            base_url=os.path.join(settings.MEDIA_URL, 'survey', 'pdfs'),
        )

        super(SurveyBaseForm, self).__init__(*args, **kwargs)
        self.create_questions()

    def get_questions(self):
        return self.survey.questions.all()

    def create_questions(self):
        for question in self.get_questions().order_by('order'):
            self.create_field(name=question.name,
                              field_type=question.type,
                              label=question.label,
                              required=question.required,
                              help_text=question.help_text,
                              intro=question.intro,
                              question=question,)

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

    def clean(self):
        clean_data = super().clean()
        self.validate_predefined_fields()
        return clean_data

    def validate_predefined_fields(self):
        for f_name, answer in self.cleaned_data.items():
            question = Question.objects.get(name=f_name,
                                            survey=self.survey)

            if question.required is False and not answer:
                continue

            if question.type == Question.PREDEFIENED_CPF:
                try:
                    cpf_validator(answer)
                except forms.ValidationError:
                    raise forms.ValidationError({f_name: 'CPF Inválido.'})

            if question.type == Question.PREDEFIENED_CNPJ:
                try:
                    cnpj_validator(answer)
                except forms.ValidationError:
                    raise forms.ValidationError({f_name: 'CNPJ Inválido.'})


class SurveyAnswerForm(SurveyBaseForm):
    """ Formulário Dinâmico. """

    def __init__(self, name=None, *args, **kwargs):
        self.answer_service_list = []
        self.name = name
        super().__init__(*args, **kwargs)

    def clean(self):
        clean_data = super().clean()
        self.answer_service_list = self._clean_answers()
        return clean_data

    def _clean_answers(self) -> list:
        """

        :return: list: uma lista de objetos do tipo Answer que corresponde a
                        todas as respostas das perguntas deste formulario.

        :raises ValidationError: exception sobe caso o serviço de resposta
        não consiga validar corretamente.
        """

        answer_list = []

        for question, answer in self.cleaned_data.items():

            if not answer:
                continue

            if not self.author and self.user:
                self.author = Author.objects.get_or_create(
                    survey=self.survey,
                    user=self.user
                )[0]

            if self.author is None and self.name:
                self.author = Author.objects.get_or_create(
                    survey=self.survey,
                    name=self.name,
                )[0]

            if self.author is None:
                raise Exception(
                    'Não foi possivel resgatar ou criar um autor'
                )

            question = Question.objects.get(
                name=question,
                survey=self.survey,
            )

            existing_answer = None

            try:
                existing_answer = Answer.objects.get(
                    question=question.pk,
                    question__survey=self.survey,
                    author=self.author,
                )
            except Answer.DoesNotExist:
                pass

            if existing_answer:
                answer_service = AnswerService(
                    instance=existing_answer,
                    data={
                        'question': question.pk,
                        'author': self.author.pk,
                        'value': answer,
                    }
                )
            else:
                answer_service = AnswerService(data={
                    'question': question.pk,
                    'author': self.author.pk,
                    'value': answer,
                })

            if answer_service.is_valid():
                answer_object = answer_service.save()
                answer_list.append(answer_object)
            else:
                raise ValidationError(answer_service.errors)

        return answer_list

    def save(self):
        with atomic():

            for answer in self.answer_service_list:

                question = answer.question
                if question.type == Question.FIELD_INPUT_FILE_PDF:
                    if question.name not in self.files:
                        continue

                    uploaded_file = self.files.get(question.name)
                    filename = self.storage.save(
                        os.path.join(str(question.pk), uploaded_file.name),
                        uploaded_file
                    )
                    answer.value = os.path.join(
                        'survey',
                        'pdfs',
                        filename
                    )

                answer.save()


class ActiveSurveyAnswerForm(SurveyAnswerForm):
    """ Formulário Dinâmico. """

    def get_questions(self):
        questions_qs = super().get_questions()
        questions_qs = questions_qs.filter(active=True)

        return questions_qs
