from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import FormView


class EventFormView(LoginRequiredMixin, FormView):
    template_name = 'gatheros_event/event/form.html'
