from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.views import View, generic

from gatheros_event.models import Event
from gatheros_event.views.mixins import AccountMixin, DeleteViewMixin
from gatheros_subscription import forms
from gatheros_subscription.models import Lot


# @TODO Resolver inconsistências de Base


class BaseLotView(AccountMixin, View):
    event = None

    def dispatch(self, request, *args, **kwargs):
        try:
            self._set_event()
        except Event.DoesNotExist:
            messages.warning(
                request,
                "Evento não informado."
            )
            return redirect(reverse_lazy('event:event-list'))

        else:
            if not self.can_view():
                return redirect(reverse(
                    'event:event-panel',
                    kwargs={'pk': self.event.pk}
                ))

        return super(BaseLotView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        # noinspection PyUnresolvedReferences
        context = super(BaseLotView, self).get_context_data(**kwargs)
        context['event'] = self.event
        return context

    def _set_event(self):
        self.event = Event.objects.get(pk=self.kwargs.get('event_pk'))

    def can_view(self, show_message=True):
        if not self.event:
            return False

        by_lots = self.event.subscription_type == Event.SUBSCRIPTION_BY_LOTS
        same_organization = self.event.organization == self.organization
        can_manage = self.request.user.has_perm(
            'gatheros_event.view_lots',
            self.event
        )
        can = by_lots and same_organization and can_manage

        if not can and show_message:
            messages.warning(
                self.request,
                "Você não pode realizar esta ação de lote neste evento."
            )

        return can


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
        context['can_add'] = self._can_add

        return context

    def _can_add(self):
        return self.request.user.has_perm(
            'gatheros_event.add_lot',
            self.event
        )


class LotAddFormView(BaseFormLotView, generic.CreateView):
    form_class = forms.LotForm
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
            'subscription:lot-list',
            kwargs={'event_pk': self.event.pk}
        )

    def can_view(self, show_message=True):
        can_view = super(LotAddFormView, self).can_view(False)
        can = can_view and self.request.user.has_perm(
            'gatheros_event.can_add_lot',
            self.event
        )

        if not can and show_message:
            messages.warning(
                self.request,
                "Você não pode adicionar lote neste evento."
            )

        return can


class LotEditFormView(BaseFormLotView, generic.UpdateView):
    show_not_allowed_message = True
    form_class = forms.LotForm
    model = forms.LotForm.Meta.model
    template_name = 'gatheros_subscription/lot/form.html'
    pk_url_kwarg = 'lot_pk'

    def get_context_data(self, **kwargs):
        context = super(LotEditFormView, self).get_context_data(**kwargs)
        context['form_title'] = "Editar lote de '{}'".format(self.event.name)
        return context

    def form_valid(self, form):
        try:
            response = super(LotEditFormView, self).form_valid(form)

        except Exception as e:
            messages.error(self.request, str(e))
            return self.form_invalid(form)

        else:
            messages.success(self.request, 'Lote alterado com sucesso.')
            return response

    def get_success_url(self):
        return reverse(
            'subscription:lot-list',
            kwargs={'event_pk': self.event.pk}
        )

    def can_view(self, show_message=True):
        can_view = super(LotEditFormView, self).can_view(False)
        can = can_view and self.request.user.has_perm(
            'gatheros_subscription.change_lot',
            self.get_object()
        )

        if not can and show_message:
            messages.warning(
                self.request,
                "Você não pode editar lote neste evento."
            )

        return can


class LotDeleteView(BaseLotView, DeleteViewMixin):
    model = Lot
    pk_url_kwarg = 'lot_pk'
    delete_message = "Tem certeza que deseja excluir o lote \"{name}\"?"
    success_message = "Lote excluído com sucesso!"

    def get_success_url(self):
        return reverse(
            'subscription:lot-list',
            kwargs={'event_pk': self.kwargs['event_pk']}
        )

    def can_view(self, show_message=True):
        self.object = self.get_object()
        can_view = super(LotDeleteView, self).can_view(False)
        can = can_view and self.can_delete()

        if not can and show_message:
            messages.warning(
                self.request,
                "Você não pode excluir lote neste evento."
            )

        return can
