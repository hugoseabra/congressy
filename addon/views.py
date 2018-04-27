from django.shortcuts import get_object_or_404
from django.views import generic

from gatheros_subscription.models import LotCategory
from .models import Product


"""
DEV NOTES: What am I doing here and how do I continue?

    Well this View is responsible for two things, rendering a list of the 
    currently selected optional products, how the hell does it do this? 
    Well, we fetch it from a session variable called product_storage, 
    and set that in the view as 'self.storage' in the __ini__ constructor 
    for processing during the GET or later use in the POST.
    
    GET requests always return HTML.
    
    POST requests are responsible for checking for conflicts and resolving 
    them by removing conflicting products from our self.storage. 

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
            LIST OPCIONAIS DO EVENTO EM COMPARAÇÃO COM PERSISTÊNCIA VOLÁTIL
            DE OUTRA LISTA DE OPCIONAIS.

            - persistência volátil: session
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
