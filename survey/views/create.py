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

    def render_to_response(self, context, **response_kwargs):
        if self.request.is_ajax():
            self.template_name = 'survey/fields.html'

        response = super().render_to_response(context, **response_kwargs)

        return response

    def post(self, *args, **kwargs):


        print('hello world')