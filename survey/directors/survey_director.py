"""
    Intenção: Este diretor tem a intenção de integrar o módulo neste módulo
    'survey' neste módulo de hotsite.
"""
import os
import absoluteuri

from gatheros_event.models import Event
from gatheros_subscription.models import EventSurvey
from survey.forms import SurveyAnswerForm, ActiveSurveyAnswerForm
from survey.models import Author, Answer

from django.conf import settings
from django.core.files.storage import FileSystemStorage


class InitialStorage(object):
    def __init__(self, storage, file_name, file_path):
        self.file_name = file_name
        self.url = absoluteuri.build_absolute_uri(storage.url(file_path))

    def __str__(self):
        return self.file_name


class SurveyDirector(object):
    """
        Implementação principal do diretor conforme as especificações do módulo
    """

    def __init__(self, event, user=None) -> None:
        """

        Este construtor tem como intenção buscar todos os objetos de survey
        que estão vinculados a um evento.

        :param event: uma instância  de um evento.
        :param user: uma instância de um usuario na plataforma.
        """

        if not isinstance(event, Event):
            msg = '{} não é uma instância de Event'.format(
                event.__class__.__name__)
            raise ValueError(msg)

        self.event = event
        self.user = user
        self.event_surveys = EventSurvey.objects.filter(event=self.event)

        super().__init__()

    def get_forms(self) -> list:
        """

        Este método é responsável por retornar uma lista de objetos do tipo
        'SurveyForm' este objeto que em si é uma instância de 'forms.Form'.

        Esses objetos da lista já devem vir 'populados' quando o usuário
        passado via parâmetro possua algum autoria de qualquer respostas(
        'answer') de um formulário('survey').

        :return: survey_forms_list: uma lista de formulários de survey
        """

        survey_forms_list = []

        for event_survey in self.event_surveys:
            """
                Iterar sobre todos os surveys de um evento.
            """

            survey = event_survey.survey  # instancia de um formulário

            try:
                """
                    Resgatar a autoria para poder popular as respostas dos
                    objetos de 'survey'
                """
                author = Author.objects.get(survey=survey, user=self.user)

                answers = {}  # lista que guarda as respostas dessa autoria

                for question in event_survey.survey.questions.all():
                    """
                        Tenta iterar sobre todas as respostas deste autor.
                    """
                    try:
                        answer = Answer.objects.get(question=question,
                                                    author=author)

                        if not answer.value:
                            continue

                        question = answer.question
                        is_multiple = \
                            question.type == question.FIELD_CHECKBOX_GROUP

                        if is_multiple:
                            value = answer.value.split(',')
                        else:
                            value = answer.value

                        answers.update({question.name: value})

                    except Answer.DoesNotExist:
                        pass

                if any(answers):
                    survey_forms_list.append(SurveyAnswerForm(
                        survey=event_survey.survey, initial=answers))
            except Author.DoesNotExist:
                survey_forms_list.append(SurveyAnswerForm(
                    survey=event_survey.survey))

        return survey_forms_list

    def get_form(self, survey, author=None, data=None) -> SurveyAnswerForm:
        """

        Este método é responsável por retornar um objeto do tipo
        'SurveyForm' este objeto que em si é uma instância de 'forms.Form'.

        Esse objeto já deve vir 'populado' quando o usuário
        passado via parâmetro possua algum autoria de qualquer resposta(
        'answer') de um formulário('survey').


        :param survey: uma instância de um objeto de formulário
        :param author: uma instância de um objeto de Author já existente
        :param data: um dict contendo as novas respostas que serão
                vinculadas ao form

        :return SurveyForm: um objeto de SurveyForm
        """

        if author is None:
            try:
                author = Author.objects.get(survey=survey, user=self.user)
            except Author.DoesNotExist:
                pass

        answers = {}  # lista que guarda as respostas dessa autoria caso haja.

        if author:
            for question in survey.questions.all():
                """
                    Tenta iterar sobre todas as respostas deste autor.
                """
                try:
                    answer = Answer.objects.get(question=question,
                                                author=author)
                    answers.update({question.name: answer.value})
                except Answer.DoesNotExist:
                    pass

        if any(answers):
            return SurveyAnswerForm(
                survey=survey,
                initial=answers,
                data=data,
                user=self.user,
                author=author,
            )

        return SurveyAnswerForm(
            survey=survey,
            data=data,
            user=self.user,
            author=author,
        )

    def get_active_form(self, survey, author=None, data=None, files=None, update=False) -> ActiveSurveyAnswerForm:
        """

        Este método é responsável por retornar um objeto do tipo
        'SurveyForm' este objeto que em si é uma instância de 'forms.Form'.

        Esse objeto já deve vir 'populado' quando o usuário
        passado via parâmetro possua algum autoria de qualquer resposta(
        'answer') de um formulário('survey').


        :param survey: uma instância de um objeto de formulário
        :param author: uma instância de um objeto de Author já existente
        :param data: um dict contendo as novas respostas que serão
                vinculadas ao form
        :param files: um dict contendo os arquivos enviados na request
        :param update: boolean informando se o resgate do formulário é para
               atualização ou não.

        :return SurveyForm: um objeto de SurveyForm
        """

        if author is None:
            try:
                author = Author.objects.get(survey=survey, user=self.user)
            except Author.DoesNotExist:
                pass

        answers = {}  # lista que guarda as respostas dessa autoria caso haja.
        if author:
            try:
                """
                    Resgatar a autoria para poder popular as respostas dos
                    objetos de 'survey'
                """
                for question in survey.questions.all():
                    """
                        Tenta iterar sobre todas as respostas deste autor.
                    """
                    try:
                        answer = Answer.objects.get(question=question,
                                                    author=author)

                        if question.type == question.FIELD_INPUT_FILE_PDF:
                            if update is True or data or files:
                                continue

                            storage = FileSystemStorage(
                                base_url=os.path.join(settings.MEDIA_URL),
                            )
                            storage.open(answer.value)

                            initial_storage = InitialStorage(
                                storage,
                                answer.human_display,
                                answer.value
                            )
                            answers.update({question.name: initial_storage})
                            continue
                        elif question.type == question.FIELD_CHECKBOX_GROUP:
                            # Must be a list to render in widget
                            answer.value = answer.value.split(',')

                        answers.update({question.name: answer.value})

                    except Answer.DoesNotExist:
                        pass

            except Author.DoesNotExist:
                pass

        if any(answers):
            return ActiveSurveyAnswerForm(
                survey=survey,
                initial=answers,
                data=data,
                user=self.user,
                author=author,
                files=files,
            )

        return ActiveSurveyAnswerForm(
            survey=survey,
            data=data,
            user=self.user,
            author=author,
            files=files,
        )
