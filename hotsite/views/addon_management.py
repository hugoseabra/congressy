from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.views import generic

from gatheros_subscription.models import LotCategory
from addon.helpers import has_quantity_conflict
from addon.models import Product

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
    template_name = "optionals/product_list.html"

    def get(self, request, *args, **kwargs):

        self.storage = self.request.session.get('product_storage')

        category_pk = kwargs.get('category_pk')
        category = get_object_or_404(LotCategory, pk=category_pk)
        self.available_options = []

        if self.storage:

            for item in self.storage:
                try:
                    optional = Product.objects.get(pk=item,
                                                   lot_category=category)
                    self.available_options.append(optional)
                except Product.DoesNotExist:
                    pass
        else:
            event_optionals_products = Product.objects.filter(
                lot_category=category, published=True)

            for optional in event_optionals_products:
                self.available_options.append(optional)

        context = self.get_context_data()
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)

        if self.available_options:
            context_data['object_list'] = self.available_options

        return context_data

    def post(self, request, *args, **kwargs):

        category_pk = kwargs.get('category_pk')
        category = get_object_or_404(LotCategory, pk=category_pk)
        session_altered = False

        product_storage = request.session.get('product_storage')

        if not product_storage:
            self.storage = []
        else:
            self.storage = product_storage

        optional_id = request.POST.get('optional_id')

        if not optional_id:
            return HttpResponse(status=400)

        new_product = get_object_or_404(Product, pk=optional_id)

        if has_quantity_conflict(new_product):
            session_altered = True
            self.storage = [item.pk for item in self.storage if
                            not new_product]
        else:
            session_altered = True
            self.storage.append(new_product.pk)

        request.session['product_storage'] = self.storage

        if session_altered:
            return HttpResponse(status=201)

        return HttpResponse(status=200)
