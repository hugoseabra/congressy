from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import generic
from django.contrib import messages

from gatheros_event.helpers.account import update_account
from gatheros_event.views.mixins import AccountMixin
from gatheros_event.models import Event
from gatheros_subscription.models import LotCategory


class LotCategoryListView(AccountMixin, generic.ListView):
    """Lista de lotes de acordo com o evento do contexto"""
    model = LotCategory
    template_name = 'lotcategory/list.html'
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

        else:
            update_account(
                request=self.request,
                organization=self.event.organization,
                force=True
            )

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        # noinspection PyUnresolvedReferences
        context = super().get_context_data(**kwargs)
        context['event'] = self.event
        return context

    def get_queryset(self):
        """Lotes a exibir são de acordo com o evento e não-interno"""
        query_set = super().get_queryset()
        return query_set.filter(event=self.event)
