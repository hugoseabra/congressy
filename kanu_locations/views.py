from unidecode import unidecode
from rest_framework import generics
from rest_framework import viewsets

from kanu_datatable import DataTableAPIView

from .models import City
from .serializers import CitySerializer


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
