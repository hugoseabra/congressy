from gatheros_subscription.models import Subscription
from survey.forms import SurveyForm
from survey.models import Author, Answer, Survey


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

    def get_form(self, survey: Survey, data=None) -> SurveyForm:
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
        # Caso não seja passado uma inscrição, resgatar apenas um
        # SurveyForm vazio
        if self.subscription is None or self.subscription.author is None:
            return SurveyForm(
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
            return SurveyForm(
                survey=survey,
                initial=answers,
                data=data,
                author=author,
            )

        return SurveyForm(
            survey=survey,
            data=data,
            author=author,
        )
