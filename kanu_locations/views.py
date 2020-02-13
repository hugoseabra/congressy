from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from unidecode import unidecode
from rest_framework import generics, status
from rest_framework import viewsets

from kanu_datatable import DataTableAPIView

from .models import City
from .serializers import CitySerializer
from .zip_code import ZipCode
from .zip_code.exceptions import CongressyAPIException, CongressyException


class CityListView(DataTableAPIView, generics.RetrieveAPIView,
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


@api_view(['GET'])
@permission_classes((AllowAny,))
def get_zip_code(request, zip_code_number):
    zip_code = ZipCode(zip_code=zip_code_number)

    try:
        zip_code.process()
    except CongressyException:
        msg = {'detail': ['CEP inválido']}
        return Response(msg, status=status.HTTP_404_NOT_FOUND)

    return Response(data=zip_code.data)
