from django.shortcuts import get_object_or_404
from django.views import generic

from gatheros_subscription.models import LotCategory
from .models import Product


"""
DEV NOTES: 

    O que estou fazendo aqui?

    Bem, esta View é responsável por duas coisas, fazendo uma lista dos
    produtos opcionais atualmente selecionados, como diabos isso acontece?
    Bem, nós buscamos por uma variável de sessão chamada 'product_storage',
    e defina isso na exibição como 'self.storage' no construtor __ini__
    para processamento durante o GET ou posterior uso no POST.
    
    Solicitações GET sempre retornam HTML.
    
    As solicitações POST são responsáveis ​​por verificar conflitos e 
    ás resolver removendo produtos conflitantes da nossa variavel de sessão.

"""


class EventProductOptionalManagementView(generic.TemplateView):
    available_options = []
    storage = None
    template_name = "optionals/product_list.html"

    def __init__(self, *args, **kwargs):
        self.storage = self.request.session.get('product_storage')
        super().__init__(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        """

        """

        category_pk = kwargs.get('category_pk')
        category = get_object_or_404(LotCategory, pk=category_pk)

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
#     def post(self, request, *args, **kwargs):
#
#         """
#             Persistir opcionais selecionadas em persistência volátil
#         """
#         if not hasattr(self.storage, 'optionals'):
#             self.storage.optionals = {}
#
#         optional_id = request.POST.get('optional_id')
#
#         try:
#             optional = Optional.objects.get(
#                 pk=optional_id,
#                 lot_category__event=self.event,
#                 published=True
#             )
#         except Optional.DoesNotExist:
#             # retornar excepção para usuário informanco que optional não é
#             # válida.
#
#         self.storage.optionals[optional.pk] = optional
#
#         # retornar 201
