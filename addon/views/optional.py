from django.contrib import messages
from django.urls import reverse
from django.views import generic
from django.db.models import Count

from addon import services
from addon.models import Product, Service
from core.views.mixins import TemplateNameableMixin
from gatheros_event.views.mixins import EventViewMixin
from ticket.models import Ticket
from .mixins import (
    ProductFeatureFlagMixin,
    ServiceFeatureFlagMixin,
)


class OptionalServiceListView(ServiceFeatureFlagMixin,
                              TemplateNameableMixin,
                              EventViewMixin,
                              generic.ListView):
    queryset = Ticket.objects.all()
    template_name = 'addon/optional/manage-service.html'

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.annotate(
            num_services=Count('addon_services'),
        ).filter(event_id=self.event.pk, num_services__gt=0)

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
        queryset = self.event.tickets

        for ticket in queryset.all():
            for optional in ticket.addon_services.all():
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
                              EventViewMixin,
                              generic.ListView):
    queryset = Ticket.objects.all()
    template_name = 'addon/optional/manage-product.html'

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.annotate(
            num_products=Count('addon_products'),
        ).filter(event_id=self.event.pk, num_products__gt=0)

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
        queryset = self.event.tickets

        for ticket in queryset.all():
            for optional in ticket.addon_products.all():
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
                             EventViewMixin,
                             generic.CreateView):
    form_class = services.ProductService
    template_name = 'addon/optional/form-product.html'

    def get_success_url(self):
        url = reverse('addon:optional-product-list', kwargs={
            'event_pk': self.event.pk
        })

        if self.object and self.object.pk:
            url += '#ticket=' + str(self.object.ticket_id)

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

            messages.success(
                self.request,
                'Produto/Serviço opcional criado com sucesso.'
            )

        except Exception as e:
            messages.error(self.request, str(e))
            return self.form_invalid(form)

        return response


class OptionalAddServiceView(ServiceFeatureFlagMixin,
                             EventViewMixin,
                             generic.CreateView):
    form_class = services.ServiceService
    template_name = 'addon/optional/form-service.html'

    def get_success_url(self):
        url = reverse('addon:optional-service-list', kwargs={
            'event_pk': self.event.pk
        })

        if self.object and self.object.pk:
            url += '#ticket=' + str(self.object.ticket_id)

        return url

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['optional_active'] = 'service'
        context['themes'] = self.event.themes.all()
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

            messages.success(
                self.request,
                'Atividade extra Opcional criado com sucesso.'
            )

        except Exception as e:
            messages.error(self.request, str(e))
            return self.form_invalid(form)

        return response


class OptionalProductEditView(ProductFeatureFlagMixin,
                              EventViewMixin,
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
            url += '#ticket=' + str(self.object.ticket_id)

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
                              EventViewMixin,
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
            url += '#ticket=' + str(self.object.ticket_id)

        return url

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object'] = self.get_object()
        context['optional_active'] = 'service'
        context['themes'] = self.event.themes.all()
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
        messages.success(
            self.request,
            'Atividade Extra alterada com sucesso.'
        )
        return super().form_valid(form)
