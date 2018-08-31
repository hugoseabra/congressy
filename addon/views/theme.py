from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse_lazy, reverse
from django.views import generic

from addon import services
from addon.models import Theme
from gatheros_event.models import Event
from gatheros_event.views.mixins import AccountMixin, DeleteViewMixin
from gatheros_event.helpers.event_business import event_has_had_payment

class ThemeListView(AccountMixin, generic.ListView):
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
        context['event_has_had_payments'] = event_has_had_payment(self.event)
        context['event'] = self.event
        context['has_paid_lots'] = self.has_paid_lots()
        return context

    def has_paid_lots(self):
        """ Retorna se evento possui algum lote pago. """
        for lot in self.event.lots.all():

            price = lot.price

            if price and price > 0:
                return True

        return False

    def get_queryset(self):
        """Lotes a exibir são de acordo com o evento e não-interno"""
        query_set = super().get_queryset()
        return query_set.filter(event=self.event).order_by('pk')


class ThemeAddView(AccountMixin, generic.CreateView):
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
        context['has_paid_lots'] = self.has_paid_lots()
        return context

    def has_paid_lots(self):
        """ Retorna se evento possui algum lote pago. """
        for lot in self.event.lots.all():

            price = lot.price

            if price and price > 0:
                return True

        return False

    def post(self, request, *args, **kwargs):
        data = request.POST
        data = data.copy()
        data.update({'event': self.event.pk})
        request.POST = data
        return super().post(request, *args, **kwargs)


class ThemeEditView(AccountMixin, generic.UpdateView):
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
        context['has_paid_lots'] = self.has_paid_lots()
        return context

    def has_paid_lots(self):
        """ Retorna se evento possui algum lote pago. """
        for lot in self.event.lots.all():

            price = lot.price

            if price and price > 0:
                return True

        return False

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


class ThemeDeleteView(DeleteViewMixin):
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
