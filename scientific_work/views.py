import os
from django.conf import settings
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.http.response import HttpResponse
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from formtools.wizard.views import SessionWizardView

from gatheros_event.views.mixins import AccountMixin
from gatheros_subscription.models import Subscription
from . import forms

FORMS = [
    ("work", forms.NewWorkForm),
    ("author", forms.AuthorForm),
]

TEMPLATES = {
    "work": "scientific_work/work_form.html",
    "author": 'scientific_work/author_form.html'
}


class WorkAddFormView(AccountMixin, SessionWizardView):
    file_storage = FileSystemStorage(
        location=os.path.join(settings.MEDIA_ROOT, 'artigos'))
    subscription = None

    def dispatch(self, request, *args, **kwargs):
        subscription_pk = self.kwargs.get('subscription_pk')
        if not subscription_pk:
            messages.error(self.request, 'Não foi possivel resgatar o evento.')
            return redirect(reverse_lazy('front:start'))

        self.subscription = get_object_or_404(Subscription, pk=subscription_pk)
        response = super().dispatch(request, *args, **kwargs)

        return response

    def get_form_kwargs(self, step=None):
        kwargs = super().get_form_kwargs(step)

        if step == 'work':
            kwargs['subscription'] = self.subscription

        return kwargs

    def get_template_names(self):
        return [TEMPLATES[self.steps.current]]

    def done(self, form_list, **kwargs):
        messages.success(self.request, 'Submissão realizado com sucesso.')
        return HttpResponse('fuck')
