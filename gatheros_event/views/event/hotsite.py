from django.conf import settings
from django.contrib import messages
from django.shortcuts import reverse, get_object_or_404
from django.views.generic import FormView

from gatheros_event import forms
from gatheros_event.helpers.account import update_account
from gatheros_event.helpers.event_business import event_has_had_payment
from gatheros_event.models import Event, Info
from gatheros_event.views.mixins import AccountMixin


class EventHotsiteView(AccountMixin, FormView):
    form_class = forms.HotsiteForm
    template_name = 'event/hotsite.html'
    event = None

    def can_access(self):
        if not self.event:
            return False

        return self.event.organization == self.organization

    def get_permission_denied_url(self):
        return reverse('event:event-list')

    def pre_dispatch(self, request):
        event = self._get_event()

        update_account(
            request=self.request,
            organization=event.organization,
            force=True
        )

        return super().pre_dispatch(request)

    def _get_event(self):
        if self.event:
            return self.event

        self.event = get_object_or_404(Event, pk=self.kwargs.get('pk'))
        return self.event

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        event = self._get_event()
        kwargs['event'] = event

        try:
            kwargs['instances'] = {
                'info': event.info if hasattr(event, 'info') else None,
                'place': event.place if hasattr(event, 'place') else None,
            }
        except Info.DoesNotExist:
            pass

        return kwargs

    def form_valid(self, form):
        messages.success(
            self.request,
            "Configurações de páginas atualizadas com sucesso."
        )
        form.save()
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.warning(self.request, 'Verifique os campos abaixo.')
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        event = self._get_event()

        context = super().get_context_data(**kwargs)
        context['has_inside_bar'] = True
        context['active'] = 'pagina-do-evento'
        context['event'] = event
        context['google_maps_api_key'] = settings.GOOGLE_MAPS_API_KEY
        context['event_has_had_payments'] = event_has_had_payment(event)

        try:
            context['info'] = event.info
        except Info.DoesNotExist:
            pass

        return context

    def get_success_url(self):
        return reverse('event:event-hotsite', kwargs={
            'pk': self.kwargs['pk']
        })
