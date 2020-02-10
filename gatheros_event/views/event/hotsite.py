from django.conf import settings
from django.contrib import messages
from django.shortcuts import reverse, get_object_or_404
from django.views.generic import FormView

from gatheros_event import forms
from gatheros_event.helpers.account import update_account
from gatheros_event.helpers.event_business import is_paid_event
from gatheros_event.models import Event, Info
from gatheros_event.views.mixins import AccountMixin, EventDraftStateMixin


class EventHotsiteView(AccountMixin, FormView, EventDraftStateMixin):
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
        context['is_paid_event'] = is_paid_event(event)

        context.update(self.get_event_state_context_data(event))

        try:
            context['info'] = event.info
        except Info.DoesNotExist:
            pass

        return context

    def get_success_url(self):
        return reverse('event:event-hotsite', kwargs={
            'pk': self.kwargs['pk']
        })


class EventHotsite2View(AccountMixin, FormView, EventDraftStateMixin):
    form_class = forms.HotsiteForm2
    template_name = 'event/hotsite2.html'
    event = None

    def can_access(self):
        if not self.event:
            return False

        return self.event.organization == self.organization

    def get_permission_denied_url(self):
        return reverse('event:event-panel', kwargs={'pk': self.event.pk})

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
        context['is_paid_event'] = is_paid_event(event)

        context.update(self.get_event_state_context_data(event))

        if hasattr(event, 'info'):
            context['info'] = event.info

        if hasattr(event, 'place'):
            context['place'] = event.place

        return context

    def get_success_url(self):
        return reverse('event:event-hotsite2', kwargs={
            'pk': self.kwargs['pk']
        })


class EventHotsiteBannerView(AccountMixin, FormView, EventDraftStateMixin):
    form_class = forms.BannerForm
    template_name = 'event/hotsite-banner.html'
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

        if hasattr(event, 'info'):
            kwargs['instance'] = event.info

        return kwargs

    def form_valid(self, form):
        messages.success(
            self.request,
            "Banner redefinido com sucesso."
        )
        form.save()
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.warning(self.request, 'Verifique o banner enviado.')
        print(form.errors)
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        event = self._get_event()

        context = super().get_context_data(**kwargs)

        context['has_inside_bar'] = True
        context['active'] = 'pagina-do-evento'
        context['event'] = event
        context['is_paid_event'] = is_paid_event(event)

        context.update(self.get_event_state_context_data(event))

        if hasattr(event, 'info'):
            context['info'] = event.info

        return context

    def get_success_url(self):
        return reverse('event:event-hotsite-banner', kwargs={
            'pk': self.kwargs['pk']
        })
