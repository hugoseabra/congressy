from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.views import generic

from addon.helpers import get_all_options
from addon.models import Product, Service, SubscriptionProduct, \
    SubscriptionService
from gatheros_subscription.models import Subscription

"""
DEV NOTES: 

    O que estou fazendo aqui?

    Solicitações GET sempre retornam HTML.
    Solicitações POST sempre retornam apenas um código de resposta HTTP.

    Bem, esta View é responsável por duas coisas, fazendo uma lista dos
    produtos opcionais atualmente selecionados, como diabos isso acontece?
    Bem, nós buscamos por uma variável de sessão chamada 'product_storage',
    e defina isso na exibição como 'self.storage' no construtor __ini__
    para processamento durante o GET ou posterior uso no POST.

    As solicitações POST são responsáveis receber uma variavel via o 
    array de POST chamado 'optional_id' e usa também uma variável de sessão 
    chamada 'product_storage'​​por verificar conflitos e ás resolver removendo
    produtos conflitantes da nossa variavel de sessão. Dependendo do 
    resultado dessa resolução de conflitos, retornamos uma resposta HTTP 
    vazia, marcando apenas o código de resposta para representar se deu tudo 
    certo.

"""


class ProductOptionalManagementView(generic.TemplateView):
    available_options = []
    storage = None
    fetch_in_storage = False
    template_name = "optionals/available_product_list.html"

    def get(self, request, *args, **kwargs):

        subscription_pk = kwargs.get('subscription_pk')
        subscription = get_object_or_404(Subscription, pk=subscription_pk)

        category = subscription.lot.category

        self.available_options = []

        self.fetch_in_storage = self.request.GET.get('fetch_in_storage')
        # @TODO add user validation here, only if request.user == sub.user

        all_products_selected_by_the_user = \
            SubscriptionProduct.objects.filter(
                subscription=subscription,
                optional__lot_category=subscription.lot.category
            )

        if self.fetch_in_storage:
            for item in all_products_selected_by_the_user:
                self.available_options.append({'optional': item.optional})

        else:
            event_optionals_products = Product.objects.filter(
                lot_category=category, published=True)

            for optional in event_optionals_products:

                contains = False

                for product in subscription.subscription_products.all():
                    if product.optional == optional:
                        contains = True

                if not contains:
                    available = not optional.has_quantity_conflict and \
                                not optional.has_sub_end_date_conflict

                    self.available_options.append({
                        'optional': optional,
                        'available': available, })

        context = self.get_context_data()
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)

        if self.available_options and len(self.available_options) > 0:
            context_data['object_list'] = self.available_options

        return context_data

    def get_template_names(self):

        template_name = super().get_template_names()

        if self.fetch_in_storage:
            template_name = "optionals/currently_selected_product_list.html"

        return template_name

    def post(self, request, *args, **kwargs):

        """
            @TODO: IMPLEMENT SOME VALIDATION BEFORE CREATING!!!!!!!!
        """

        subscription_pk = kwargs.get('subscription_pk')
        optional_id = self.request.POST.get('optional_id')
        action = self.request.POST.get('action')

        if not optional_id or not subscription_pk or not action:
            return HttpResponse(status=400)

        product = get_object_or_404(Product, pk=int(optional_id))
        subscription = get_object_or_404(Subscription, pk=subscription_pk)

        if action == 'add':
            _, created = SubscriptionProduct.objects.get_or_create(
                optional=product,
                subscription=subscription,
                optional_price=product.price,
                optional_liquid_price=product.liquid_price,
            )

            if created:
                return HttpResponse('201 OK', status=201)
        elif action == 'remove':
            subscription_product = get_object_or_404(SubscriptionProduct,
                                                     optional=product,
                                                     subscription=subscription)
            subscription_product.delete()
            return HttpResponse('201 OK', status=201)

        return HttpResponse('200 OK', status=200)


class ServiceOptionalManagementView(generic.TemplateView):
    available_options = []
    storage = None
    fetch_in_storage = False
    template_name = "optionals/available_services_list.html"

    def get(self, request, *args, **kwargs):

        try:
            subscription_pk = kwargs.get('subscription_pk')
            subscription = Subscription.objects.get(pk=subscription_pk)

            category = subscription.lot.category
            self.available_options = []

            self.fetch_in_storage = self.request.GET.get('fetch_in_storage')
            all_selected_services = SubscriptionService.objects.filter(
                subscription=subscription,
                optional__lot_category=subscription.lot.category
            )
            # @TODO add user validation here, only if request.user == sub.user

            if self.fetch_in_storage:
                for item in all_selected_services:
                    self.available_options.append({'optional': item.optional})
            else:

                # All service optionals
                all_services = Service.objects.filter(
                    lot_category=category, published=True)
                pre_selected_services = subscription.subscription_services.all()

                available = get_all_options(all_services,
                                            pre_selected_services,
                                            available_only=False)

                self.available_options = available

        except Subscription.DoesNotExist:
            pass

        context = self.get_context_data()
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)

        if self.available_options and len(self.available_options) > 0:
            context_data['object_list'] = self.available_options

        return context_data

    def get_template_names(self):

        template_name = super().get_template_names()

        if self.fetch_in_storage:
            template_name = "optionals/currently_selected_service_list.html"

        return template_name

    def post(self, request, *args, **kwargs):

        """
            @TODO: IMPLEMENT SOME VALIDATION BEFORE CREATING!!!!!!!!
        """

        subscription_pk = kwargs.get('subscription_pk')
        optional_id = self.request.POST.get('optional_id')
        action = self.request.POST.get('action')

        if not optional_id or not subscription_pk or not action:
            return HttpResponse(status=400)

        service = get_object_or_404(Service, pk=int(optional_id))
        subscription = get_object_or_404(Subscription, pk=subscription_pk)

        if action == 'add':
            _, created = SubscriptionService.objects.get_or_create(
                optional=service,
                subscription=subscription,
                optional_price=service.price,
                optional_liquid_price=service.liquid_price,
            )

            if created:
                return HttpResponse('201 OK', status=201)
        elif action == 'remove':
            subscription_service = get_object_or_404(SubscriptionService,
                                                     optional=service,
                                                     subscription=subscription)
            subscription_service.delete()
            return HttpResponse('201 OK', status=201)

        return HttpResponse('200 OK', status=200)
