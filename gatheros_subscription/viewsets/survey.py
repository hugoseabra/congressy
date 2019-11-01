from rest_framework import viewsets, permissions, status
from rest_framework.response import Response

from gatheros_event.models import Event
from gatheros_subscription.models import EventSurvey
from gatheros_subscription.serializers import EventSurveySerializer
from gatheros_subscription.serializers.survey import QuestionSerializer
from survey.models import Question, Survey
from .mixins import RestrictionViewMixin

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
        return self.is_user_subscribed(event_id) is True

    def can_manage_object(self, event_id):
        is_member = self.is_user_event_member(event_id)
        is_subscribed = self.is_user_subscribed(event_id)

        return is_member is True or is_subscribed is True


class EventSurveyViewSet(RestrictionViewMixin,
                         InstanceManagementMixin,
                         viewsets.ModelViewSet):
    serializer_class = EventSurveySerializer
    queryset = EventSurvey.objects.all()
    permission_classes = (
        permissions.IsAuthenticated,
    )

    def list(self, request, *args, **kwargs):

        event_id = request.query_params.get('event', None)

        if event_id is None:
            content = {
                'detail': ['missing event in query string', ]
            }

            return Response(content, status=status.HTTP_400_BAD_REQUEST)

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


class QuestionViewSet(RestrictionViewMixin,
                      InstanceManagementMixin,
                      viewsets.ModelViewSet):
    serializer_class = QuestionSerializer
    queryset = Question.objects.all()
    permission_classes = (
        permissions.IsAuthenticated,
    )

    def get_event_id_by_survey(self, survey_id):
        try:
            survey = Survey.objects.get(pk=survey_id)
            return survey.event.event_id

        except Question.DoesNotExist:
            return None

    def list(self, request, *args, **kwargs):

        survey_id = self.kwargs.get('survey_pk')

        if survey_id is None:
            content = {
                'detail': ['Você não pode acessar perguntas por este endpoint']
            }

            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        event_id = self.get_event_id_by_survey(survey_id)
        if self.can_manage_list(event_id) is False:
            content = {
                'detail': ['Você não pode acessar formulários deste evento.']
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
