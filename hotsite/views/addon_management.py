import json

from django.core import serializers
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.views import generic

from addon.helpers import has_quantity_conflict, has_sub_end_date_conflict
from addon.models import Product
from gatheros_subscription.models import LotCategory

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


class EventProductOptionalManagementView(generic.TemplateView):
    available_options = []
    storage = None
    template_name = "optionals/available_product_list.html"

    def get(self, request, *args, **kwargs):

        self.storage = self.request.session.get('product_storage')

        category_pk = kwargs.get('category_pk')
        category = get_object_or_404(LotCategory, pk=category_pk)
        self.available_options = []

        fetch_in_storage = self.request.GET.get('fetch_in_storage')

        if fetch_in_storage:

            if self.storage:

                for item in self.storage:
                    try:
                        optional = Product.objects.get(pk=item,
                                                       lot_category=category)
                        self.available_options.append({'optional': optional})
                    except Product.DoesNotExist:
                        pass

            return_format = self.request.GET.get('format')

            if return_format and return_format == 'json':

                json_list = []

                for product in self.available_options:
                    json_list.append(
                        self.create_product_json(product['optional']))
                return JsonResponse(json_list, safe=False)

        else:
            event_optionals_products = Product.objects.filter(
                lot_category=category, published=True)

            for optional in event_optionals_products:

                if not self.storage or optional.pk not in self.storage:
                    available = not has_quantity_conflict(optional) and \
                                not has_sub_end_date_conflict(optional)

                    self.available_options.append({'optional': optional,
                                                   'available': available})

        context = self.get_context_data()
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)

        if self.available_options:
            context_data['object_list'] = self.available_options

        return context_data

    def post(self, request, *args, **kwargs):

        optional_id = request.POST.get('optional_id')
        action = request.POST.get('action')
        new_product = get_object_or_404(Product, pk=optional_id)

        if not optional_id:
            return HttpResponse(status=400)

        optional_id = int(optional_id)

        session_altered = False

        product_storage = request.session.get('product_storage')

        if not product_storage:
            self.storage = []
        else:
            self.storage = product_storage

        if action and action == 'add':
            if optional_id not in self.storage:
                if not has_quantity_conflict(new_product) and not \
                        has_sub_end_date_conflict(new_product):
                    session_altered = True
                    self.storage.append(new_product.pk)
        elif action and action == 'remove':
            if optional_id in self.storage:
                session_altered = True
                self.storage.remove(optional_id)

        request.session['product_storage'] = self.storage

        if session_altered:
            return HttpResponse(status=201)

        return HttpResponse(status=200)

    def get_template_names(self):

        template_name = super().get_template_names()

        fetch_in_storage = self.request.GET.get('fetch_in_storage')

        if fetch_in_storage:
            template_name = "optionals/currently_selected_product_list.html"

        return template_name

    # @TODO not DRY, fix
    def create_product_json(self, product):

        remove_fields = [
            'lot_category',
            'created_by',
            'modified_by',
            'created',
            'modified',
            'release_days',
            'optional_type',
            'quantity',
            'date_end_sub',
            'published',
        ]

        product_obj_as_json = serializers.serialize('json', [product, ])
        product_obj = json.loads(product_obj_as_json)
        product_obj = product_obj[0]
        product_obj = product_obj['fields']
        product_obj['id'] = product.pk

        for field in remove_fields:
            del product_obj[field]

        return product_obj
