from decimal import Decimal

from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.views import View, generic

from gatheros_event.helpers.account import update_account
from gatheros_event.models import Event, Organization
from gatheros_event.views.mixins import AccountMixin, DeleteViewMixin
from gatheros_subscription import forms
from gatheros_subscription.models import Lot, EventSurvey
from core.views.mixins import TemplateNameableMixin


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
            update_account(
                request=self.request,
                organization=self.event.organization,
                force=True
            )

        if not self.can_view():
            return redirect('event:event-list')

        return super(BaseLotView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        # noinspection PyUnresolvedReferences
        context = super(BaseLotView, self).get_context_data(**kwargs)
        context['event'] = self.event
        context['has_paid_lots'] = self.has_paid_lots()
        return context

    def _set_event(self):
        self.event = Event.objects.get(pk=self.kwargs.get('event_pk'))

    def has_paid_lots(self):
        """ Retorna se evento possui algum lote pago. """
        for lot in self.event.lots.all():
            if lot.price is None:
                continue

            if lot.price > 0:
                return True

        return False

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


class BaseFormLotView(BaseLotView, generic.FormView):
    def get_initial(self):
        # noinspection PyUnresolvedReferences
        initial = super(BaseFormLotView, self).get_initial()
        initial['event'] = self.event.pk

        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['congressy_minimum_price'] = settings.CONGRESSY_MINIMUM_AMOUNT
        context['congressy_plan_percent'] = self.event.congressy_percent
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        if self.request.method in ('POST', 'PUT'):
            data = self.request.POST.copy()

            if 'price' in data and data.get('price') is not None:
                price = data.get('price').replace('.', '').replace(',', '.')
                if price:
                    data['price'] = Decimal(price)

            kwargs.update({
                'data': data,
            })

        return kwargs


class LotListView(TemplateNameableMixin, BaseLotView, generic.ListView):
    """Lista de lotes de acordo com o evento do contexto"""
    template_name = 'lot/manage.html'
    queryset = Lot.objects.filter(category__isnull=True).order_by(
        'date_start',
        'date_end'
    )

    def get_queryset(self):
        """Lotes a exibir são de acordo com o evento e não-interno"""
        query_set = super(LotListView, self).get_queryset()
        return query_set.filter(event=self.event, internal=False).order_by(
            'date_start', 'date_end'
        )

    def get_context_data(self, **kwargs):
        context = super(LotListView, self).get_context_data(**kwargs)
        context['event'] = self.event
        context['can_add'] = self._can_add
        context['subscription_stats'] = self.get_subscription_stats()
        context['full_banking'] = self._get_full_banking()
        context['exhibition_code'] = Lot.objects.generate_exhibition_code()
        context['categories'] = self.event.lot_categories.all().order_by('pk')

        return context

    def get_subscription_stats(self):
        stats = {
            'num': {},
            'remaining': {},
        }
        queryset = self.event.lot_categories

        for cat in queryset.all():
            for lot in cat.lots.all():
                sub_queryset = lot.subscriptions.filter(
                    completed=True,
                    status__in=['confirmed', 'awaiting']
                )
                num = sub_queryset.count()
                stats['num'][lot.pk] = num
                if lot.limit is not None:
                    if num > int(lot.limit):
                        stats['remaining'][lot.pk] = 0
                    else:
                        stats['remaining'][lot.pk] = int(lot.limit) - num

        return stats

    def _get_full_banking(self):

        if not self.organization:
            return False

        banking_required_fields = ['bank_code', 'agency', 'account',
                                   'cnpj_ou_cpf', 'account_type']

        for field in Organization._meta.get_fields():
            for required_field in banking_required_fields:
                if field.name == required_field:
                    if not getattr(self.organization, field.name):
                        return False

        return True

    def _can_add(self):
        return self.request.user.has_perm(
            'gatheros_event.can_add_lot',
            self.event
        )


class LotAddFormView(BaseFormLotView, generic.CreateView):
    form_class = forms.LotForm
    # template_name = 'gatheros_subscription/lot/form.html'
    template_name = 'lot/form.html'
    cat_pk = None

    def get_context_data(self, **kwargs):
        context = super(LotAddFormView, self).get_context_data(**kwargs)
        context['form_title'] = "Novo lote para '{}'".format(self.event.name)
        context['full_banking'] = self._get_full_banking()
        context['has_surveys'] = self._event_has_surveys()
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Lote criado com sucesso.')
        return super(LotAddFormView, self).form_valid(form)

    def get_success_url(self):
        url = reverse(
            'subscription:lot-list',
            kwargs={'event_pk': self.event.pk}
        )
        if self.cat_pk is not None:
            url += '#cat='+self.cat_pk

        return url

    def post(self, request, *args, **kwargs):
        if 'limit_switch' not in request.POST:
            request.POST = request.POST.copy()
            request.POST['limit'] = 0

        if 'category' in self.request.POST:
            self.cat_pk = self.request.POST.get('category')

        return super().post(request, *args, **kwargs)

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

    def _get_full_banking(self):

        if not self.organization:
            return False

        banking_required_fields = ['bank_code', 'agency', 'account',
                                   'cnpj_ou_cpf', 'account_type']

        for field in Organization._meta.get_fields():

            for required_field in banking_required_fields:

                if field.name == required_field:

                    if not getattr(self.organization, field.name):
                        return False

        return True

    def _event_has_surveys(self):
        all_surveys = EventSurvey.objects.filter(event=self.event).count()
        return all_surveys > 0


class LotEditFormView(BaseFormLotView, generic.UpdateView):
    show_not_allowed_message = True
    form_class = forms.LotForm
    model = forms.LotForm.Meta.model
    template_name = 'lot/form.html'
    pk_url_kwarg = 'lot_pk'
    cat_pk = None

    def get_context_data(self, **kwargs):
        context = super(LotEditFormView, self).get_context_data(**kwargs)
        context['form_title'] = "Editar lote de '{}'".format(self.event.name)
        context['full_banking'] = self._get_full_banking()
        context['has_surveys'] = self._event_has_surveys()
        context['has_subscriptions'] = self.object.subscriptions.filter(
            completed=True,
        ).count() > 0

        return context

    def post(self, request, *args, **kwargs):
        if 'limit_switch' not in request.POST:
            request.POST = request.POST.copy()
            request.POST['limit'] = 0

        if 'category' in self.request.POST:
            self.cat_pk = self.request.POST.get('category')

        return super().post(request, *args, **kwargs)

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
        url = reverse(
            'subscription:lot-list',
            kwargs={'event_pk': self.event.pk}
        )
        if self.cat_pk is not None:
            url += '#cat=' + self.cat_pk

        return url

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

    def _get_full_banking(self):

        if not self.organization:
            return False

        banking_required_fields = [
            'bank_code',
            'agency',
            'account',
            'cnpj_ou_cpf',
            'account_type',
            'bank_account_id'
        ]

        for field in Organization._meta.get_fields():

            for required_field in banking_required_fields:

                if field.name == required_field:

                    if not getattr(self.organization, field.name):
                        return False

        return True

    def _event_has_surveys(self):
        all_surveys = EventSurvey.objects.filter(event=self.event).count()
        return all_surveys > 0


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
