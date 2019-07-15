from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.response import Response

from gatheros_event.models import Event
from gatheros_subscription.models import EventSurvey
from survey.models import Survey
from ticket.models import Ticket
from ticket.serializers import TicketSerializer


class TicketChangeSurveyAPIView(generics.RetrieveUpdateAPIView):
    """
        Endpoint usado para alterar o Survey de determinado lote.
    """
    http_method_names = ['get', 'patch']
    serializer_class = TicketSerializer
    lookup_url_kwarg = 'ticket_pk'

    def __init__(self, **kwargs):
        self.event = None
        self.survey = None
        self.ticket = None
        super().__init__(**kwargs)


    def dispatch(self, request, *args, **kwargs):
        event_pk = kwargs.pop('event_pk')
        ticket_pk = kwargs.get('ticket_pk')
        survey_pk = kwargs.get('survey_pk', False)

        if event_pk is None or ticket_pk is None:
            return Response(status=404)

        self.event = get_object_or_404(Event, pk=event_pk)
        self.ticket = get_object_or_404(Ticket,
                                        pk=ticket_pk,
                                        event_id=event_pk)

        if survey_pk:
            self.survey = get_object_or_404(Survey, pk=survey_pk,)

        return super().dispatch(request, *args, **kwargs)

    def get_object(self):
        return self.ticket

    def get_queryset(self):
        return Ticket.objects.filter(event_id=self.event.pk)

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
