from django import forms
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.utils.module_loading import import_string
from django.views import View, generic

from gatheros_event.models import Event
from gatheros_event.views.mixins import AccountMixin
from gatheros_subscription.models import Lot

DeleteViewMixin = import_string('core.view.delete.DeleteViewMixin')


# @TODO Levar forms para raiz forms.py
# @TODO Resolver inconsistências de Base

class BaseLotView(AccountMixin, View):
    event = None
    show_not_allowed_message = False

    def dispatch(self, request, *args, **kwargs):
        try:
            self._set_event()
        except Event.DoesNotExist:
            messages.warning(
                request,
                "Evento não informado."
            )
            return redirect(reverse_lazy('gatheros_event:event-list'))

        else:
            if self._cannot_view():
                return redirect(reverse(
                    'gatheros_event:event-panel',
                    kwargs={'pk': self.event.pk}
                ))

        return super(BaseLotView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        # noinspection PyUnresolvedReferences
        context = super(BaseLotView, self).get_context_data(**kwargs)
        context['event'] = self.event
        return context

    def _set_event(self):
        self.event = Event.objects.get(pk=self.kwargs.get('pk'))

    def _cannot_view(self):
        if not self.event:
            return True

        by_lots = self.event.subscription_type == Event.SUBSCRIPTION_BY_LOTS
        same_organization = self.event.organization == self.organization
        can = by_lots and same_organization

        if can is False and self.show_not_allowed_message:
            messages.warning(
                self.request,
                "Você não pode inserir gerenciar lotes neste evento."
            )

        return can is False


class BaseFormLotView(BaseLotView):
    def get_initial(self):
        # noinspection PyUnresolvedReferences
        initial = super(BaseFormLotView, self).get_initial()
        initial['event'] = self.event

        return initial


class LotListView(BaseLotView, generic.ListView):
    """Lista de lotes de acordo com o evento do contexto"""
    model = Lot
    template_name = 'gatheros_subscription/lot/list.html'
    ordering = ['name']

    def get_queryset(self):
        """Lotes a exibir são de acordo com o evento e não-interno"""
        query_set = super(LotListView, self).get_queryset()
        return query_set.filter(event=self.event, internal=False)

    def get_context_data(self, **kwargs):
        context = super(LotListView, self).get_context_data(**kwargs)
        context['event'] = self.event

        return context


class LotForm(forms.ModelForm):
    event = None

    class Meta:
        model = Lot
        fields = [
            'event',
            'name',
            'date_start',
            'date_end',
            'limit',
            'price',
            'discount_type',
            'discount',
            'transfer_tax',
            'private'
        ]
        widgets = {'event': forms.HiddenInput()}

    def __init__(self, **kwargs):
        super(LotForm, self).__init__(**kwargs)
        self.event = kwargs.get('initial').get('event')
        self._set_dates_help_texts()

    def _set_dates_help_texts(self):
        last_lot = self.event.lots.last()
        if last_lot:
            diff = self.event.date_start - last_lot.date_end

            if diff.days <= 1:
                date_start_help = 'O lote anterior ({}) pega todo o período' \
                                  ' do evento.'.format(last_lot.name)
            else:
                lot_date_end = last_lot.date_end.strftime('%d/%m/%Y %Hh%M')
                date_start_help = \
                    'Existe um lote anterior ({}) que finaliza em {}. Tente' \
                    ' não chocar as datas.'.format(last_lot.name, lot_date_end)

            self.fields['date_start'].help_text = date_start_help

        event_date_start = self.event.date_start.strftime('%d/%m/%Y %Hh%M')
        self.fields['date_end'].help_text = \
            'O evento inicia-se em {}. O final do lote deve ser anterior a' \
            ' esta data.'.format(event_date_start)


class LotAddFormView(BaseFormLotView, generic.CreateView):
    show_not_allowed_message = True
    form_class = LotForm
    template_name = 'gatheros_subscription/lot/form.html'

    def get_context_data(self, **kwargs):
        context = super(LotAddFormView, self).get_context_data(**kwargs)
        context['form_title'] = "Novo lote para '{}'".format(self.event.name)
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Lote criado com sucesso.')
        return super(LotAddFormView, self).form_valid(form)

    def get_success_url(self):
        return reverse(
            'gatheros_subscription:lot-list',
            kwargs={'pk': self.event.pk}
        )


class LotEditFormView(BaseFormLotView, generic.UpdateView):
    show_not_allowed_message = True
    form_class = LotForm
    model = LotForm.Meta.model
    template_name = 'gatheros_subscription/lot/form.html'
    pk_url_kwarg = 'lot_pk'

    def get_context_data(self, **kwargs):
        context = super(LotEditFormView, self).get_context_data(**kwargs)
        context['form_title'] = "Editar lote de '{}'".format(self.event.name)
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Lote editado com sucesso.')
        return super(LotEditFormView, self).form_valid(form)

    def get_success_url(self):
        return reverse(
            'gatheros_subscription:lot-list',
            kwargs={'pk': self.event.pk}
        )


class LotDeleteView(DeleteViewMixin):
    model = Event
    pk_url_kwarg = 'lot_pk'
    delete_message = "Não é possível excluir o lote '{name}' possivelmente" \
                     " porque inscrições. Exporte, gerencie e" \
                     " exclua as inscrições existentes antes de excluir o" \
                     " lote."

    success_message = "Lote excluído com sucesso!"

    def get_success_url(self):
        return reverse(
            'gatheros_subscription:lot-list',
            kwargs={'pk': self.kwargs['pk']}
        )
