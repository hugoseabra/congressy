from django.contrib import messages
from django.core.exceptions import ImproperlyConfigured
from django.shortcuts import redirect, reverse
from django.urls import reverse_lazy
from django.views.generic import DetailView

from gatheros_event import forms
from gatheros_event.models import Event
from gatheros_event.views.mixins import AccountMixin


def update_banners(request, **kwargs):
    try:
        pk = kwargs.get('pk')
        event = Event.objects.get(pk=pk)
    except Event.DoesNotExist:
        messages.warning(
            request,
            "Evento inválido."
        )
        return redirect(reverse('gatheros_event:event-list'))

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
        messages.error(request, form.errors)
        messages.error(request, form.non_field_errors())

    return redirect(reverse('gatheros_event:event-detail', kwargs={'pk': pk}))


def update_place(request, **kwargs):
    try:
        pk = kwargs.get('pk')
        event = Event.objects.get(pk=pk)
    except Event.DoesNotExist:
        messages.warning(
            request,
            "Evento inválido."
        )
        return redirect(reverse('gatheros_event:event-list'))

    form = forms.EventPlaceForm(instance=event, data=request.POST)
    if form.is_valid():
        form.save()
        messages.success(request, "Local atualizado com sucesso.")
    else:
        messages.error(request, "Local não atualizado.")
        messages.error(request, form.errors)
        messages.error(request, form.non_field_errors())

    return redirect(reverse('gatheros_event:event-detail', kwargs={'pk': pk}))


class EventDetailView(AccountMixin, DetailView):
    model = forms.EventBannerForm.Meta.model
    template_name = 'gatheros_event/event/detail.html'
    object = None

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        if not self._can_view():
            return redirect(reverse_lazy('gatheros_event:event-list'))

        return super(EventDetailView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(EventDetailView, self).get_context_data(**kwargs)
        context['banner_form'] = forms.EventBannerForm(instance=self.object)
        context['place_form'] = forms.EventPlaceForm(instance=self.object)
        return context

    # noinspection PyMethodMayBeStatic,PyUnusedLocal
    def post(self, request, *args, **kwargs):
        data = request.POST.copy()
        submit_type = data.get('submit_type')
        supported_types = ('update_banners', 'update_place')

        if not submit_type \
                or (submit_type not in supported_types) \
                and not callable(submit_type):
            raise ImproperlyConfigured(
                'Formulário não configurado corretamente. Insira um campo'
                ' do tipo `hidden` com um dos seguintes tipos: ' +
                ', '.join(supported_types)
            )

        submit_type = eval(submit_type)
        return submit_type(request, **kwargs)

    def _can_view(self):
        can_edit = self.request.user.has_perm(
            'gatheros_event.change_event',
            self.object
        )
        same_organization = self.object.organization == self.organization
        return can_edit and same_organization
