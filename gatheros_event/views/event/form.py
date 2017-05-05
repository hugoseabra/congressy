from django.views.generic import FormView

class EventFormView(FormView):
    template_name = 'gatheros_event/event/form.html'
