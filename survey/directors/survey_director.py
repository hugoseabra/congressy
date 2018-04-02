"""
    Intenção: Este diretor tem a intenção de integrar o módulo neste módulo
    'survey' neste módulo de hotsite.
"""
from gatheros_event.models import Event
from gatheros_subscription.models import EventSurvey
from survey.forms import SurveyForm
from survey.models import Author, Answer


class SurveyDirector(object):
    """
        Implementação principal do diretor conforme as especificações do módulo
    """

    def __init__(self, event, user) -> None:
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
                        answers.update({question.name: answer.value})
                    except Answer.DoesNotExist:
                        pass

                if any(answers):
                    survey_forms_list.append(SurveyForm(
                        survey=event_survey.survey, initial=answers))
            except Author.DoesNotExist:
                survey_forms_list.append(SurveyForm(
                    survey=event_survey.survey))

        return survey_forms_list

    def get_form(self, survey, data={}) -> SurveyForm:
        """

        Este método é responsável por retornar um objeto do tipo
        'SurveyForm' este objeto que em si é uma instância de 'forms.Form'.

        Esse objeto já deve vir 'populado' quando o usuário
        passado via parâmetro possua algum autoria de qualquer resposta(
        'answer') de um formulário('survey').


        :param survey: uma instância de um objeto de formulário
        :param data: um dict contendo as novas respostas que serão
                vinculadas ao form

        :return SurveyForm: um objeto de SurveyForm
        """

        try:
            author = Author.objects.get(survey=survey, user=self.user)
        except Author.DoesNotExist:
            author = None

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
                        answers.update({question.name: answer.value})
                    except Answer.DoesNotExist:
                        pass

            except Author.DoesNotExist:
                pass

        if any(answers):
            return SurveyForm(
                survey=survey,
                initial=answers,
                data=data,
                user=self.user
            )

        return SurveyForm(
            survey=survey,
            data=data,
            user=self.user
        )
