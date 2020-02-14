from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import generics, status
from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from unidecode import unidecode

from kanu_datatable import DataTableAPIView
from .models import City
from .serializers import CitySerializer
from .zip_code import ZipCodeViaCep as ZipCode
from .zip_code.exceptions import CongressyException


class CityListView(DataTableAPIView,
                   generics.RetrieveAPIView,
                   viewsets.GenericViewSet):
    """
    Rota para pesquisar e recuperar Cidades

    - **Procurar:**  ?&q=Goiania&uf=GO
    """
    queryset = City.objects.all()
    serializer_class = CitySerializer
    order_columns = ['uf', 'name']
    search_fields = ['name', 'uf', 'id']

    def get_queryset(self):
        qs = City.objects.all()

        if self.request.GET.get('q', ''):
            qs = qs.filter(
                name_ascii__icontains=unidecode(self.request.GET.get('q')))

        if self.request.GET.get('uf', ''):
            qs = qs.filter(uf=self.request.GET.get('uf'))

        return qs


class ZipCodeViewSet(viewsets.ViewSet):
    permission_classes = (AllowAny,)

    # Cache requested url for each user for 2 hours
    @method_decorator(cache_page(60 * 60 * 24 * 10))
    def list(self, request, *args, **kwargs):
        zip_code_number = self.kwargs.get('zip_code_number')

        zip_code = ZipCode(zip_code=zip_code_number)

        try:
            zip_code.process()
        except CongressyException:
            msg = {'detail': ['CEP inválido']}
            return Response(msg, status=status.HTTP_404_NOT_FOUND)

        return Response(data=zip_code.data)
