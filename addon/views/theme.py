from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse_lazy, reverse
from django.views import generic

from addon import services
from addon.models import Theme
from addon.views.mixins import ServiceFeatureFlagMixin
from gatheros_event.helpers.event_business import is_paid_event
from gatheros_event.models import Event
from gatheros_event.views.mixins import DeleteViewMixin, \
    EventDraftStateMixin


class ThemeMixin(ServiceFeatureFlagMixin, EventDraftStateMixin):
    pass


class ThemeListView(ThemeMixin, generic.ListView):
    """Lista de lotes de acordo com o evento do contexto"""
    model = Theme
    template_name = 'addon/theme/list.html'
    ordering = ['name']
    event = None

    def dispatch(self, request, *args, **kwargs):
        try:
            self.event = Event.objects.get(pk=self.kwargs.get('event_pk'))

        except Event.DoesNotExist:
            messages.warning(
                request,
                "Evento não informado."
            )
            return redirect(reverse_lazy('event:event-list'))

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        # noinspection PyUnresolvedReferences
        context = super().get_context_data(**kwargs)
        context['has_inside_bar'] = True
        context['active'] = 'addon-themes'
        context['is_paid_event'] = is_paid_event(self.event)
        context['event'] = self.event
        return context

    def get_queryset(self):
        """Lotes a exibir são de acordo com o evento e não-interno"""
        query_set = super().get_queryset()
        return query_set.filter(event=self.event).order_by('pk')


class ThemeAddView(ThemeMixin, generic.CreateView):
    form_class = services.ThemeService
    template_name = 'addon/theme/form.html'
    event = None

    def dispatch(self, request, *args, **kwargs):
        try:
            self.event = Event.objects.get(pk=self.kwargs.get('event_pk'))

        except Event.DoesNotExist:
            messages.warning(
                request,
                "Evento não informado."
            )
            return redirect(reverse_lazy('event:event-list'))

        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('addon:theme-list', kwargs={
            'event_pk': self.event.pk,
        })

    def form_valid(self, form):
        try:
            response = super().form_valid(form)

        except Exception as e:
            messages.error(self.request, str(e))
            return self.form_invalid(form)

        messages.success(self.request, 'Tema criado com sucesso.')
        return response

    def get_context_data(self, **kwargs):
        # noinspection PyUnresolvedReferences
        context = super().get_context_data(**kwargs)
        context['event'] = self.event
        context['active'] = 'service'
        return context

    def post(self, request, *args, **kwargs):
        data = request.POST
        data = data.copy()
        data.update({'event': self.event.pk})
        request.POST = data
        return super().post(request, *args, **kwargs)


class ThemeEditView(ThemeMixin, generic.UpdateView):
    form_class = services.ThemeService
    model = services.ThemeService.manager_class.Meta.model
    template_name = 'addon/theme/form.html'
    event = None

    def dispatch(self, request, *args, **kwargs):
        try:
            self.event = Event.objects.get(pk=self.kwargs.get('event_pk'))

        except Event.DoesNotExist:
            messages.warning(
                request,
                "Evento não informado."
            )
            return redirect(reverse_lazy('event:event-list'))

        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('addon:theme-list', kwargs={
            'event_pk': self.event.pk,
        })

    def get_context_data(self, **kwargs):
        # noinspection PyUnresolvedReferences
        context = super().get_context_data(**kwargs)
        context['event'] = self.event
        context['active'] = 'service'
        return context

    def post(self, request, *args, **kwargs):
        data = request.POST
        data = data.copy()
        data.update({'event': self.event.pk})
        request.POST = data
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        try:
            response = super().form_valid(form)

        except Exception as e:
            messages.error(self.request, str(e))
            return self.form_invalid(form)

        messages.success(
            self.request,
            'Tema alterado com sucesso.'
        )
        return response


class ThemeDeleteView(ThemeMixin, DeleteViewMixin):
    model = services.ThemeService.manager_class.Meta.model
    delete_message = "Tem certeza que deseja excluir o tema \"{name}\"?"
    success_message = "Categoria excluída com sucesso!"

    def get_success_url(self):
        return reverse(
            'addon:theme-list',
            kwargs={'event_pk': self.kwargs['event_pk']}
        )

    def can_delete(self):
        obj = self.get_object()
        return obj.is_deletable()
