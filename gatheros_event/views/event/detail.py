from django.contrib import messages
from django.core.exceptions import ImproperlyConfigured
from django.shortcuts import redirect, reverse
from django.views.generic import DetailView

from gatheros_event import forms
from gatheros_event.models import Event
from gatheros_event.views.mixins import AccountMixin


def update_event_banners(request, **kwargs):
    pk = kwargs.get('pk')
    if not pk:
        messages.warning(
            request,
            "Nenhum evento informado."
        )
        return redirect(reverse('gatheros_event:event-list'))

    try:
        event = Event.objects.get(pk=pk)
    except Event.DoesNotExist:
        messages.warning(
            request,
            "Evento inválido."
        )
        return redirect(reverse('gatheros_event:event-list'))
    else:
        form = forms.EventBannerForm(
            instance=event,
            data=request.POST,
            files=request.FILES
        )
        if form.is_valid():
            form.save()
            messages.success(request, "Banners atualizados com sucesso.")
        else:
            messages.error(request, "Dados não atualizados.")

    return redirect(reverse('gatheros_event:event-detail', kwargs={'pk': pk}))


class EventDetailView(AccountMixin, DetailView):
    model = forms.EventBannerForm.Meta.model
    template_name = 'gatheros_event/event/detail.html'
    object = None

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super(EventDetailView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(EventDetailView, self).get_context_data(**kwargs)
        context['banner_form'] = forms.EventBannerForm(instance=self.object)
        return context

    # noinspection PyMethodMayBeStatic,PyUnusedLocal
    def post(self, request, *args, **kwargs):
        data = request.POST.copy()
        submit_type = data.get('submit_type')
        supported_types = ('update_banners',)

        if not submit_type or (submit_type not in supported_types):
            raise ImproperlyConfigured(
                'Formulário não configurado corretamente. Insira um campo'
                'do tipo `hidden` com um dos seguintes tipos: '
                + ', '.join(supported_types)
            )

        func = None
        if submit_type == 'update_banners':
            func = update_event_banners

        return func(request, **kwargs)
