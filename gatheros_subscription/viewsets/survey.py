from rest_framework import viewsets, permissions, status
from rest_framework.response import Response

from gatheros_subscription.models import EventSurvey
from gatheros_subscription.serializers import EventSurveySerializer
from gatheros_subscription.serializers.survey import QuestionSerializer
from survey.models import Question
from .mixins import RestrictionViewMixin


class EventSurveyViewSet(RestrictionViewMixin, viewsets.ModelViewSet):
    serializer_class = EventSurveySerializer
    queryset = EventSurvey.objects.all()
    permission_classes = (
        permissions.IsAuthenticated,
    )

    def get_queryset(self):
        user = self.request.user

        org_pks = list()

        if hasattr(user, 'person'):

            for m in user.person.members.filter(active=True):
                org_pks.append(m.organization_id)

        queryset = super().get_queryset()
        return queryset.filter(event__organization_id__in=org_pks)

    def list(self, request, *args, **kwargs):

        event_id = request.query_params.get('event', None)

        if event_id is None:
            content = {
                'errors': ['missing event in query string', ]
            }

            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        try:
            event_id = int(event_id)
        except ValueError:
            content = {
                'errors': ["event in query is not int: '{}' ".format(
                    event_id), ]
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


class QuestionViewSet(RestrictionViewMixin, viewsets.ModelViewSet):
    serializer_class = QuestionSerializer
    queryset = Question.objects.all()
    permission_classes = (
        permissions.IsAuthenticated,
    )

    def filter_queryset(self, queryset):
        qs = super().filter_queryset(queryset)

        survey_pk = self.kwargs.get('survey_pk')

        return qs

    def list(self, request, *args, **kwargs):

        survey_id = self.kwargs.get('survey_pk')

        if survey_id is None:
            content = {
                'errors': ['missing survey_id in parameters', ]
            }

            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        try:
            survey_id = int(survey_id)
        except ValueError:
            content = {
                'errors': ["event in parameter is not"
                           " int: '{}' ".format(survey_id)]
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
