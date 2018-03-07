from django.views import generic
from gatheros_event.views.mixins import EventViewMixin


class CreateSurveyView(EventViewMixin, generic.TemplateView):
    template_name = 'survey/create.html'

    def dispatch(self, request, *args, **kwargs):

        self.event = self.get_event()

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['event'] = self.event
        return context


