from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.response import Response

from gatheros_event.models import Event
from gatheros_subscription.models import Lot, EventSurvey
from survey.models import Survey
from gatheros_subscription.serializers import LotSerializer


class LotChangeSurveyAPIView(generics.RetrieveUpdateAPIView):
    """
        Endpoint usado para alterar o Survey de determinado lote.
    """
    http_method_names = ['get', 'patch']
    serializer_class = LotSerializer
    lookup_url_kwarg = 'lot_pk'
    event = None
    survey = None
    lot = None

    def dispatch(self, request, *args, **kwargs):
        event_pk = kwargs.pop('event_pk')
        lot_pk = kwargs.get('lot_pk')
        survey_pk = kwargs.get('survey_pk', False)

        if event_pk is None or lot_pk is None:
            return Response(status=404)

        self.event = get_object_or_404(Event, pk=event_pk)
        self.lot = get_object_or_404(Lot, pk=lot_pk, event=self.event.pk)

        if survey_pk:
            self.survey = get_object_or_404(Survey, pk=survey_pk,)

        return super().dispatch(request, *args, **kwargs)

    def get_object(self):
        return self.lot

    def get_queryset(self):
        return Lot.objects.filter(event=self.event)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        # Fetch for existing event_survey or create a new one.
        if self.survey:
            try:
                event_survey = EventSurvey.objects.get(
                    survey_id=self.survey.pk,
                )
                event_survey.event = self.event
                event_survey.save()
            except EventSurvey.DoesNotExist:
                event_survey = EventSurvey.objects.create(
                    event=self.event,
                    survey=self.survey,
                )

            request.data['event_survey'] = event_survey.pk
        else:
            request.data['event_survey'] = ''

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)


