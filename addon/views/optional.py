from django.contrib import messages
from django.forms.models import model_to_dict
from django.shortcuts import redirect
from django.urls import reverse
from django.views import generic

from addon import forms
from addon.models import Product, Service
from core.views.mixins import TemplateNameableMixin
from gatheros_event.models import Event
from gatheros_event.views.mixins import AccountMixin, DeleteViewMixin
from gatheros_subscription.models import LotCategory


class EventViewMixin(AccountMixin, generic.View):
    event = None

    def dispatch(self, request, *args, **kwargs):
        try:
            self.event = Event.objects.get(pk=self.kwargs.get('event_pk'))

        except Event.DoesNotExist:
            messages.warning(
                request,
                "Evento não informado."
            )
            return redirect('event:event-list')

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        # noinspection PyUnresolvedReferences
        context = super().get_context_data(**kwargs)
        context['event'] = self.event
        return context


class OptionalServiceListView(TemplateNameableMixin,
                              EventViewMixin,
                              generic.ListView):
    queryset = LotCategory.objects.all()
    template_name = 'addon/optional/manage-service.html'

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(event=self.event)

    def get_context_data(self, **kwargs):
        # noinspection PyUnresolvedReferences
        context = super().get_context_data(**kwargs)
        context['active'] = 'service'
        context['subscription_stats'] = self.get_subscription_stats()
        return context

    def get_subscription_stats(self):
        stats = {
            'num': {},
            'remaining': {},
        }
        queryset = self.event.lot_categories

        for cat in queryset.all():
            for optional in cat.service_optionals.all():
                sub_queryset = optional.subscription_services.filter(
                    subscription__status__in=['confirmed', 'awaiting']
                )
                num = sub_queryset.count()
                stats['num'][optional.pk] = num
                if optional.quantity is not None:
                    if num > int(optional.quantity):
                        stats['remaining'][optional.pk] = 0
                    else:
                        stats['remaining'][optional.pk] = \
                            int(optional.quantity) - num

        return stats


class OptionalProductListView(TemplateNameableMixin,
                              EventViewMixin,
                              generic.ListView):
    queryset = LotCategory.objects.all()
    template_name = 'addon/optional/manage-product.html'

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(event=self.event)

    def get_context_data(self, **kwargs):
        # noinspection PyUnresolvedReferences
        context = super().get_context_data(**kwargs)
        context['active'] = 'product'
        context['subscription_stats'] = self.get_subscription_stats()
        return context

    def get_subscription_stats(self):
        stats = {
            'num': {},
            'remaining': {},
        }
        queryset = self.event.lot_categories

        for cat in queryset.all():
            for optional in cat.product_optionals.all():
                sub_queryset = optional.subscription_products.filter(
                    subscription__status__in=['confirmed', 'awaiting']
                )
                num = sub_queryset.count()
                stats['num'][optional.pk] = num
                if optional.quantity is not None:
                    if num > int(optional.quantity):
                        stats['remaining'][optional.pk] = 0
                    else:
                        stats['remaining'][optional.pk] = \
                            int(optional.quantity) - num

        return stats


class OptionalAddView(EventViewMixin, generic.CreateView):
    form_class = forms.OptionalForm
    template_name = 'addon/optional/form.html'

    def get_success_url(self):
        if isinstance(self.object, Product):
            url = reverse('addon:optional-product-list', kwargs={
                'event_pk': self.event.pk
            })
        else:
            url = reverse('addon:optional-service-list', kwargs={
                'event_pk': self.event.pk
            })

        if self.object and self.object.pk:
            url += '#cat=' + str(self.object.lot_category.pk)

        return url

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        kwargs['event'] = self.event
        return kwargs

    def get_initial(self):
        from datetime import datetime

        return {
            'name': 'My service optional',
            'lot_category': 1,
            'optional_service_type': 1,
            'theme': 1,
            'schedule_start': datetime(2018, 6, 2, 14, 00, 00),
            'schedule_end': datetime(2018, 6, 2, 15, 00, 00),
            'date_end_sub': datetime(2018, 5, 30, 23, 59, 59),
            'description': 'Some description',
            'price': '230.00',
        }

    def form_valid(self, form):
        try:
            response = super().form_valid(form)

        except Exception as e:
            messages.error(self.request, str(e))
            return self.form_invalid(form)

        messages.success(self.request, 'Opcional criado com sucesso.')
        return response


class OptionalProductEditView(EventViewMixin, generic.UpdateView):
    form_class = forms.OptionalForm
    model = Product
    template_name = 'addon/optional/form.html'
    pk_url_kwarg = 'optional_pk'
    initial = {
        'optional_kind': 'product',
    }

    def get_success_url(self):
        url = reverse('addon:optional-product-list', kwargs={
            'event_pk': self.event.pk
        })

        if self.object and self.object.pk:
            url += '#cat=' + str(self.object.lot_category.pk)

        return url

    def get_initial(self):
        initial = super().get_initial()
        initial.update({'optional_product_type': self.object.optional_type.pk})
        initial.update(model_to_dict(self.object))
        return initial

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        kwargs['event'] = self.event
        return kwargs

    def form_valid(self, form):
        try:
            response = super().form_valid(form)

        except Exception as e:
            messages.error(self.request, str(e))
            return self.form_invalid(form)

        messages.success(self.request, 'Opcional alterado com sucesso.')
        return response

    def form_invalid(self, form):
        return super().form_invalid(form)


class OptionalServiceEditView(EventViewMixin, generic.UpdateView):
    form_class = forms.OptionalForm
    model = Service
    template_name = 'addon/optional/form.html'
    pk_url_kwarg = 'optional_pk'
    initial = {
        'optional_kind': 'service',
    }

    def get_success_url(self):
        url = reverse('addon:optional-service-list', kwargs={
            'event_pk': self.event.pk
        })

        if self.object and self.object.pk:
            url += '#cat=' + str(self.object.lot_category.pk)

        return url

    def get_initial(self):
        initial = super().get_initial()
        initial.update({'optional_service_type': self.object.optional_type.pk})
        initial.update(model_to_dict(self.object))
        return initial

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        kwargs['event'] = self.event
        return kwargs

    def form_valid(self, form):
        try:
            response = super().form_valid(form)

        except Exception as e:
            messages.error(self.request, str(e))
            return self.form_invalid(form)

        messages.success(self.request, 'Opcional alterado com sucesso.')
        return response

    def form_invalid(self, form):
        return super().form_invalid(form)


class OptionalProductDeleteView(DeleteViewMixin):
    model = Product
    pk_url_kwarg = 'optional_pk'
    delete_message = "Tem certeza que deseja excluir o opcional \"{name}\"?"
    success_message = "Opcional excluído com sucesso!"

    def get_success_url(self):
        return reverse(
            'addon:optional-product-list',
            kwargs={'event_pk': self.kwargs['event_pk']}
        )

    def can_delete(self):
        obj = self.get_object()
        return obj.is_deletable()


class OptionalServiceDeleteView(DeleteViewMixin):
    model = Service
    pk_url_kwarg = 'optional_pk'
    delete_message = "Tem certeza que deseja excluir o opcional \"{name}\"?"
    success_message = "Opcional excluído com sucesso!"

    def get_success_url(self):
        return reverse(
            'addon:optional-service-list',
            kwargs={'event_pk': self.kwargs['event_pk']}
        )

    def can_delete(self):
        obj = self.get_object()
        return obj.is_deletable()
