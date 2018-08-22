from decimal import Decimal
from django.contrib import messages
from django.urls import reverse
from django.views import generic

from addon import services
from addon.models import Product, Service
from core.views.mixins import TemplateNameableMixin
from gatheros_event.models import Event
from gatheros_event.views.mixins import AccountMixin, DeleteViewMixin
from gatheros_subscription.models import LotCategory
from .mixins import (
    ProductFeatureFlagMixin,
    ServiceFeatureFlagMixin,
    EventOptionalMixin,
)

class EventOptionalMixin(AccountMixin, generic.View):
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

        paid_lots = False

        for lot in self.event.lots.all():
            if lot.price is not None and lot.price > 0:
                paid_lots = True
                break

        if paid_lots is False:
            if self.event.event_type == self.event.EVENT_TYPE_FREE:
                messages.error(
                    request,
                    "Evento grátis não possui opcionais."
                )
                return redirect('event:event-panel', self.event.pk)

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        # noinspection PyUnresolvedReferences
        context = super().get_context_data(**kwargs)
        context['event'] = self.event
        context['has_paid_lots'] = self.has_paid_lots()
        context['themes'] = self.event.themes.all()
        context['cgsy_percent'] = Decimal(self.event.congressy_percent) / 100
        return context

    def has_paid_lots(self):
        """ Retorna se evento possui algum lote pago. """
        for lot in self.event.lots.all():

            price = lot.price

            if price and price > 0:
                return True

        return False


class OptionalServiceListView(ServiceFeatureFlagMixin,
                              TemplateNameableMixin,
                              EventOptionalMixin,
                              generic.ListView):
    queryset = LotCategory.objects.all()
    template_name = 'addon/optional/manage-service.html'

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(event=self.event)

    def get_context_data(self, **kwargs):
        # noinspection PyUnresolvedReferences
        context = super().get_context_data(**kwargs)
        context['has_inside_bar'] = True
        context['active'] = 'addon-atividades-extras'

        context['optional_active'] = 'service'
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
                    subscription__test_subscription=False,
                    subscription__completed=True,
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


class OptionalProductListView(ProductFeatureFlagMixin,
                              TemplateNameableMixin,
                              EventOptionalMixin,
                              generic.ListView):
    queryset = LotCategory.objects.all()
    template_name = 'addon/optional/manage-product.html'

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(event=self.event)

    def get_context_data(self, **kwargs):
        # noinspection PyUnresolvedReferences
        context = super().get_context_data(**kwargs)
        context['optional_active'] = 'product'
        context['subscription_stats'] = self.get_subscription_stats()

        context['has_inside_bar'] = True
        context['active'] = 'addon-opcionais'

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
                    subscription__test_subscription=False,
                    subscription__completed=True,
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


class OptionalAddProductView(ProductFeatureFlagMixin,
                             EventOptionalMixin,
                             generic.CreateView):
    form_class = services.ProductService
    template_name = 'addon/optional/form-product.html'

    def get_success_url(self):
        url = reverse('addon:optional-product-list', kwargs={
            'event_pk': self.event.pk
        })

        if self.object and self.object.pk:
            url += '#cat=' + str(self.object.lot_category.pk)

        return url

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['optional_active'] = 'product'
        return context

    def post(self, request, *args, **kwargs):
        request.POST = request.POST.copy()
        request.POST.update({'created_by': request.user.first_name})
        return super().post(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['event'] = self.event
        return kwargs

    def form_valid(self, form):
        try:
            response = super().form_valid(form)

        except Exception as e:
            messages.error(self.request, str(e))
            return self.form_invalid(form)

        messages.success(
            self.request,
            'Produto/Serviço opcional criado com sucesso.'
        )
        return response

    # def get_initial(self):
    #     from datetime import timedelta
    # 
    #     initial = super().get_initial()
    #     initial.update({
    #         'name': 'Optional test',
    #         'optional_type': 1,
    #         'lot_category': 1,
    #         'price': '22,00',
    #         'date_end_sub': self.event.date_start - timedelta(minutes=1),
    #     })
    #     return initial


class OptionalAddServiceView(ServiceFeatureFlagMixin,
                             EventOptionalMixin,
                             generic.CreateView):
    form_class = services.ServiceService
    template_name = 'addon/optional/form-service.html'

    def get_success_url(self):
        url = reverse('addon:optional-service-list', kwargs={
            'event_pk': self.event.pk
        })

        if self.object and self.object.pk:
            url += '#cat=' + str(self.object.lot_category.pk)

        return url

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['optional_active'] = 'service'
        return context

    def post(self, request, *args, **kwargs):
        request.POST = request.POST.copy()
        request.POST.update({'created_by': request.user.first_name})
        return super().post(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['event'] = self.event
        return kwargs

    def form_valid(self, form):
        try:
            response = super().form_valid(form)

        except Exception as e:
            messages.error(self.request, str(e))
            return self.form_invalid(form)

        messages.success(
            self.request,
            'Atividade extra Opcional criado com sucesso.'
        )
        return response

        # def get_initial(self):
        #     from datetime import datetime, timedelta
        #
        #     initial = super().get_initial()
        #     initial.update({
        #         'name': 'Optional test',
        #         'optional_type': 1,
        #         'lot_category': 1,
        #         'theme': 1,
        #         'schedule_start': datetime.now() + timedelta(days=30),
        #         'schedule_end': datetime.now() + timedelta(days=30, hours=2),
        #         'place': 'Auditório 1 Madre Teresa',
        #         'price': '22,00',
        #         'date_end_sub': self.event.date_start - timedelta(minutes=1),
        #         'restrict_unique': True,
        #     })
        #     return initial


class OptionalProductEditView(ProductFeatureFlagMixin,
                              EventOptionalMixin,
                              generic.UpdateView):
    form_class = services.ProductService
    model = Product
    template_name = 'addon/optional/form-product.html'
    pk_url_kwarg = 'optional_pk'

    def get_success_url(self):
        url = reverse('addon:optional-product-list', kwargs={
            'event_pk': self.event.pk
        })

        if self.object and self.object.pk:
            url += '#cat=' + str(self.object.lot_category.pk)

        return url

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['event'] = self.event
        return kwargs

    def form_valid(self, form):
        try:
            response = super().form_valid(form)

        except Exception as e:
            messages.error(self.request, str(e))
            return self.form_invalid(form)

        messages.success(
            self.request,
            'Produto / Serviço Opcional alterado com sucesso.'
        )
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object'] = self.get_object()
        context['optional_active'] = 'product'
        context['optonal_has_subscriptions'] = \
            self.object.subscription_products.filter(
                subscription__completed=True,
                subscription__test_subscription=False
            ).count()
        return context

    def form_invalid(self, form):
        return super().form_invalid(form)


class OptionalServiceEditView(ServiceFeatureFlagMixin,
                              EventOptionalMixin,
                              generic.UpdateView):
    form_class = services.ServiceService
    model = Service
    template_name = 'addon/optional/form-service.html'
    pk_url_kwarg = 'optional_pk'

    def get_success_url(self):
        url = reverse('addon:optional-service-list', kwargs={
            'event_pk': self.event.pk
        })

        if self.object and self.object.pk:
            url += '#cat=' + str(self.object.lot_category.pk)

        return url

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object'] = self.get_object()
        context['optional_active'] = 'service'
        context['has_subscriptions'] = \
            self.object.subscription_services.filter(
                subscription__completed=True,
                subscription__test_subscription=False
            ).count()
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['event'] = self.event

        return kwargs

    def post(self, request, *args, **kwargs):
        request.POST = request.POST.copy()
        request.POST.update({'modified_by': request.user.first_name})
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        try:
            response = super().form_valid(form)

        except Exception as e:
            messages.error(self.request, str(e))
            return self.form_invalid(form)

        messages.success(
            self.request,
            'Atividae Extra Opcional alterado com sucesso.'
        )
        return response

    def form_invalid(self, form):
        return super().form_invalid(form)
