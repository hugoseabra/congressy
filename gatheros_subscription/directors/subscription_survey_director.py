import os

import absoluteuri
from django.conf import settings
from django.core.files.storage import FileSystemStorage

from gatheros_subscription.models import Subscription
from survey.forms import SurveyAnswerForm, SurveyBaseForm, \
    ActiveSurveyAnswerForm
from survey.models import Author, Answer, Survey, Question


class InitialStorage(object):
    def __init__(self, storage, file_name, file_path):
        self.file_name = file_name
        self.url = absoluteuri.build_absolute_uri(storage.url(file_path))

    def __str__(self):
        return self.file_name


class SubscriptionSurveyDirector(object):
    """
        Implementação principal do diretor para agir sobre o modelo que
        serve como interface a Survey, o SubscriptionAuthor
    """

    def __init__(self, subscription: Subscription = None) -> None:
        """

        Este construtor tem como intenção buscar todos os objetos de survey
        que estão vinculados a uma inscrição.

        :param subscription: uma instância  de uma inscrição.
        """

        self.subscription = subscription

        if subscription is not None:
            if not isinstance(subscription, Subscription):
                msg = '{} não é uma instância de Subscription'.format(
                    subscription.__class__.__name__)
                raise ValueError(msg)

            if self.subscription.lot.event_survey is None:
                raise Exception('Lot não possui event_survey')

            survey = self.subscription.lot.event_survey.survey
            user = None
            if self.subscription.person.user:
                user = self.subscription.person.user

            if self.subscription.author is None:
                self.subscription.author = Author.objects.create(
                    name=self.subscription.person.name,
                    survey=survey,
                    user=user,
                )
                self.subscription.save()

        super().__init__()

    def get_form(self, survey: Survey, data=None) -> SurveyAnswerForm:
        """

        Este método é responsável por retornar um objeto do tipo
        'SurveyAnswerForm' este objeto que em si é uma instância de 'forms.Form'.

        Esse objeto já deve vir 'populado' quando o usuário
        passado via parâmetro possua algum autoria de qualquer resposta(
        'answer') de um formulário('survey').

        :param survey: uma instância de um objeto de formulário
        :param data: um dict contendo as novas respostas que serão
                vinculadas ao form

        :return SurveyAnswerForm: um objeto de SurveyAnswerForm
        """
        # Caso não seja passado uma inscrição, resgatar apenas um
        # SurveyAnswerForm vazio
        if self.subscription is None or self.subscription.author is None:
            return SurveyAnswerForm(
                survey=survey,
                data=data,
            )

        answers = {}  # lista que guarda as respostas dessa autoria caso haja.
        author = self.subscription.author

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
                    answer = Answer.objects.get(
                        question=question,
                        author=author,
                        question__survey=survey,
                    )
                    answers.update({question.name: answer.value})
                except Answer.DoesNotExist:
                    pass

        except Author.DoesNotExist:
            pass

        if any(answers):
            return SurveyAnswerForm(
                survey=survey,
                initial=answers,
                data=data,
                author=author,
            )

        return SurveyAnswerForm(
            survey=survey,
            data=data,
            author=author,
        )

    def get_active_form(self, survey: Survey, data=None, files=None,
                        update=False) -> ActiveSurveyAnswerForm:
        """

        Este método é responsável por retornar um objeto do tipo
        'SurveyAnswerForm' este objeto que em si é uma instância de 'forms.Form'.

        Esse objeto já deve vir 'populado' quando o usuário
        passado via parâmetro possua algum autoria de qualquer resposta(
        'answer') de um formulário('survey').

        :param survey: uma instância de um objeto de formulário
        :param data: um dict contendo as novas respostas que serão
                vinculadas ao form

        :return SurveyAnswerForm: um objeto de SurveyAnswerForm
        """
        # Caso não seja passado uma inscrição, resgatar apenas um
        # SurveyAnswerForm vazio
        if self.subscription is None or self.subscription.author is None:
            return ActiveSurveyAnswerForm(
                survey=survey,
                data=data,
                files=files,
            )

        answers = {}  # lista que guarda as respostas dessa autoria caso haja.
        author = self.subscription.author

        """
            Resgatar a autoria para poder popular as respostas dos
            objetos de 'survey'
        """
        file_types = [
            Question.FIELD_INPUT_FILE_PDF,
            Question.FIELD_INPUT_FILE_IMAGE,
        ]

        for question in survey.questions.all():
            """
                Tenta iterar sobre todas as respostas deste autor.
            """
            try:
                answer = Answer.objects.get(
                    question=question,
                    author=author,
                    question__survey=survey,
                )

                if question.type in file_types:
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

                answers.update({question.name: answer.value})

            except Answer.DoesNotExist:
                pass

        if any(answers):
            return ActiveSurveyAnswerForm(
                survey=survey,
                initial=answers,
                data=data,
                author=author,
                files=files,
            )

        return ActiveSurveyAnswerForm(
            survey=survey,
            data=data,
            author=author,
            files=files,
        )

    def get_base_form(self, survey: Survey, data=None, files=None,
                      update=False) -> SurveyBaseForm:
        """

        Este método é responsável por retornar um objeto do tipo
        'SurveyAnswerForm' este objeto que em si é uma instância de 'forms.Form'.

        Esse objeto já deve vir 'populado' quando o usuário
        passado via parâmetro possua algum autoria de qualquer resposta(
        'answer') de um formulário('survey').

        :param survey: uma instância de um objeto de formulário
        :param data: um dict contendo as novas respostas que serão
                vinculadas ao form

        :return SurveyAnswerForm: um objeto de SurveyAnswerForm
        """
        # Caso não seja passado uma inscrição, resgatar apenas um
        # SurveyAnswerForm vazio
        if self.subscription is None or self.subscription.author is None:
            return SurveyBaseForm(
                survey=survey,
                data=data,
                files=files,
            )

        answers = {}  # lista que guarda as respostas dessa autoria caso haja.
        author = self.subscription.author

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
                    answer = Answer.objects.get(
                        question=question,
                        author=author,
                        question__survey=survey,
                    )

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

                    answers.update({question.name: answer.value})
                except Answer.DoesNotExist:
                    pass

        except Author.DoesNotExist:
            pass

        if any(answers):
            return SurveyBaseForm(
                survey=survey,
                initial=answers,
                data=data,
                author=author,
                files=files,
            )

        return SurveyBaseForm(
            survey=survey,
            data=data,
            author=author,
            files=files,
        )
