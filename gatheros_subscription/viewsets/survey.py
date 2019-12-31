import uuid

from rest_framework import viewsets, status
from rest_framework.response import Response

from core.viewsets import AuthenticatedViewSetMixin
from gatheros_event.models import Event
from gatheros_subscription.models import EventSurvey
from gatheros_subscription.serializers import (
    AnswerSerializer,
    EventSurveySerializer,
    QuestionSerializer,
    OptionSerializer,
)
from survey.models import Question, Survey, Option, Answer


class InstanceManagementMixin(object):
    def is_user_event_member(self, event_id) -> bool:
        try:
            event = Event.objects.get(pk=event_id)
            return event.organization.is_member(self.request.user) is True
        except Event.DoesNotExist:
            return False

    def is_user_subscribed(self, event_id: int):
        user = self.request.user
        if hasattr(user, 'person') is False:
            return False

        try:
            event = Event.objects.get(pk=event_id)
            sub_qs = event.subscriptions.filter(person_id=user.person.pk)
            return sub_qs.count() > 0

        except Event.DoesNotExist:
            return False

    def can_manage_list(self, event_id):
        return \
            self.is_user_subscribed(event_id) is True or \
            self.is_user_event_member(event_id)

    def can_manage_object(self, event_id):
        is_member = self.is_user_event_member(event_id)
        is_subscribed = self.is_user_subscribed(event_id)

        return is_member is True or is_subscribed is True


class EventSurveyViewSet(AuthenticatedViewSetMixin,
                         InstanceManagementMixin,
                         viewsets.ModelViewSet):
    serializer_class = EventSurveySerializer
    queryset = EventSurvey.objects.all()

    def list(self, request, *args, **kwargs):

        event_id = request.query_params.get('event', None)

        if self.can_manage_list(event_id) is False:
            content = {
                'detail': ['Você não pode acessar formulários deste evento.']
            }

            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        qs = self.get_queryset()
        qs = qs.filter(event_id=event_id)

        page = self.paginate_queryset(self.filter_queryset(qs))
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()

        if self.can_manage_object(instance.event_id) is False:
            content = {'detail': ['Você não pode acessar este formulário']}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        return super().retrieve(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        data = request.data
        event_id = data.get('event')

        if self.can_manage_object(event_id) is False:
            content = {'detail': ['Você não pode criar formulários']}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()

        if self.can_manage_object(instance.event_id) is False:
            content = {'detail': ['Você não pode editar formulários']}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        if self.can_manage_object(instance.event_id) is False:
            content = {'detail': ['Você não pode excluir formulários']}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        return super().destroy(request, *args, **kwargs)


class QuestionViewSet(AuthenticatedViewSetMixin,
                      InstanceManagementMixin,
                      viewsets.ModelViewSet):
    serializer_class = QuestionSerializer
    queryset = Question.objects.filter(active=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.subscription_valid = False

    def get_event_id_by_survey(self, survey_id):
        try:
            survey = Survey.objects.get(pk=survey_id)
            return survey.event.event_id

        except Survey.DoesNotExist:
            return None

    def get_serializer(self, *args, **kwargs):
        if self.subscription_valid is True:
            subscription_pk = \
                self.request.query_params.get('subscription', None)
            if subscription_pk:
                kwargs.update({'subscription_pk': subscription_pk})

        return super().get_serializer(*args, **kwargs)

    def list(self, request, *args, **kwargs):

        survey_id = self.kwargs.get('survey_pk')

        sub_pk = request.query_params.get('subscription', None)
        if sub_pk:
            try:
                uuid.UUID(sub_pk)
                self.subscription_valid = True
            except ValueError:
                content = {
                    'errors': [
                        "Subscription provided is a valid uuid",
                    ]
                }
                return Response(content, status=status.HTTP_400_BAD_REQUEST)

        if survey_id is None:
            content = {
                'detail': ['Você não pode acessar perguntas por este endpoint']
            }

            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        qs = self.get_queryset()
        qs = qs.filter(survey_id=survey_id)

        page = self.paginate_queryset(self.filter_queryset(qs))
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        survey_id = instance.survey_id
        event_id = self.get_event_id_by_survey(survey_id)

        if self.can_manage_object(event_id) is False:
            content = {'detail': ['Você não pode acessar este formulário']}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        return super().retrieve(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        data = request.data
        survey_id = data.get('survey')
        event_id = self.get_event_id_by_survey(survey_id)

        if self.can_manage_object(event_id) is False:
            content = {'detail': ['Você não pode criar formulários']}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        survey_id = instance.survey_id
        event_id = self.get_event_id_by_survey(survey_id)

        if self.can_manage_object(event_id) is False:
            content = {'detail': ['Você não pode editar formulários']}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        survey_id = instance.survey_id
        event_id = self.get_event_id_by_survey(survey_id)

        if self.can_manage_object(event_id) is False:
            content = {'detail': ['Você não pode excluir formulários']}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        return super().destroy(request, *args, **kwargs)


class OptionViewSet(AuthenticatedViewSetMixin,
                    InstanceManagementMixin,
                    viewsets.ModelViewSet):
    serializer_class = OptionSerializer
    queryset = Option.objects.filter(question__active=True)

    def get_question_by_id(self, question_id):
        try:
            return Question.objects.get(pk=question_id)
        except Question.DoesNotExist:
            return None

    def get_event_id_by_survey(self, survey_id):
        try:
            survey = Survey.objects.get(pk=survey_id)
            return survey.event.event_id

        except Survey.DoesNotExist:
            return None

    def list(self, request, *args, **kwargs):

        question_id = request.query_params.get('question', None)

        if question_id is None:
            content = {
                'detail': ["query string 'question' não informado."]
            }

            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        question = self.get_question_by_id(question_id)
        event_id = self.get_event_id_by_survey(question.survey_id)
        if self.can_manage_list(event_id) is False:
            content = {
                'detail': ['Você não pode acessar formulários deste evento.']
            }

            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        qs = self.get_queryset()
        qs = qs.filter(question_id=question_id)

        page = self.paginate_queryset(self.filter_queryset(qs))
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        survey_id = instance.question.survey_id
        event_id = self.get_event_id_by_survey(survey_id)

        if self.can_manage_object(event_id) is False:
            content = {'detail': ['Você não pode acessar este formulário']}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        return super().retrieve(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        data = request.data
        question_id = data.get('question')
        question = self.get_question_by_id(question_id)
        survey_id = question.survey_id
        event_id = self.get_event_id_by_survey(survey_id)

        if self.can_manage_object(event_id) is False:
            content = {'detail': ['Você não pode criar formulários']}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        survey_id = instance.question.survey_id
        event_id = self.get_event_id_by_survey(survey_id)

        if self.can_manage_object(event_id) is False:
            content = {'detail': ['Você não pode editar formulários']}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        survey_id = instance.question.survey_id
        event_id = self.get_event_id_by_survey(survey_id)

        if self.can_manage_object(event_id) is False:
            content = {'detail': ['Você não pode excluir formulários']}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        return super().destroy(request, *args, **kwargs)


class AnswerViewSet(AuthenticatedViewSetMixin,
                    InstanceManagementMixin,
                    viewsets.ModelViewSet):
    serializer_class = AnswerSerializer
    queryset = Answer.objects.filter(question__active=True)

    def get_question_by_id(self, question_id):
        try:
            return Question.objects.get(pk=question_id)
        except Question.DoesNotExist:
            return None

    def get_event_id_by_survey(self, survey_id):
        try:
            survey = Survey.objects.get(pk=survey_id)
            return survey.event.event_id

        except Survey.DoesNotExist:
            return None

    def list(self, request, *args, **kwargs):
        content = {
            'detail': ['Você não pode acessar respostas por este endpoint.']
        }

        return Response(content, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        survey_id = instance.question.survey_id
        event_id = self.get_event_id_by_survey(survey_id)

        if self.can_manage_object(event_id) is False:
            content = {'detail': ['Você não pode acessar este formulário']}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        return super().retrieve(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        data = request.data
        question_id = data.get('question')
        question = self.get_question_by_id(question_id)
        survey_id = question.survey_id
        event_id = self.get_event_id_by_survey(survey_id)

        if self.can_manage_object(event_id) is False:
            content = {'detail': ['Você não pode criar formulários']}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        survey_id = instance.question.survey_id
        event_id = self.get_event_id_by_survey(survey_id)

        if self.can_manage_object(event_id) is False:
            content = {'detail': ['Você não pode editar formulários']}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        survey_id = instance.question.survey_id
        event_id = self.get_event_id_by_survey(survey_id)

        if self.can_manage_object(event_id) is False:
            content = {'detail': ['Você não pode excluir formulários']}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        return super().destroy(request, *args, **kwargs)
