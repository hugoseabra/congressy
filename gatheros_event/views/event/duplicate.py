from django.conf import settings
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.views import generic

from gatheros_event import forms
from gatheros_event.helpers.account import update_account
from gatheros_event.views.event.form import BaseEventView


class EventDuplicateFormView(BaseEventView, generic.CreateView):
    form_class = forms.EventDuplicationForm
    template_name = 'event/duplication-form.html'

    success_message = 'Evento duplicado com sucesso.'
    form_title = 'Duplicar evento: {name} (#{id})'
    object = None

    def get_form_kwargs(self):
        kwargs = {
            'event': self.event,
            'person': self.request.user.person,
        }

        return kwargs

    def get_form(self, form_class=None):
        if not form_class:
            form_class = self.form_class

        kwargs = self.get_form_kwargs()

        if self.request.method in ('POST', 'PUT'):
            kwargs.update({
                'data': self.request.POST,
                'files': self.request.FILES,
            })

        return form_class(**kwargs)

    def form_valid(self, form):
        try:
            response = HttpResponseRedirect(self.get_success_url())
            update_account(
                request=self.request,
                organization=form.event.organization,
                force=True
            )

        except Exception as e:
            messages.error(self.request, str(e))
            return self.form_invalid(form)

        else:
            messages.success(self.request, self.success_message)
            return response

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if not form.is_valid():
            return self.render_to_response(self.get_context_data(
                form=form,
            ))

        self.event = form.save()
        return self.form_valid(form)

    def get_success_url(self):

        form = self.get_form()
        event = form.event

        if settings.DEBUG is False:
            redirect_to = reverse_lazy('public:remarketing-redirect')
            marketing_type = '?marketing_type=adwords'
            page_type = '&page_type=new_event'

            next_page = '&next=' + reverse(
                'event:event-panel',
                kwargs={'pk': event.pk}
            )

            return redirect_to + marketing_type + page_type + next_page

        return reverse('event:event-panel', kwargs={'pk': event.pk})
