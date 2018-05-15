from rest_framework import generics

from scientific_work.serializers import WorkSerializer
from scientific_work.models import Work


class WorkAPIListView(generics.ListAPIView):
    serializer_class = WorkSerializer
    queryset = Work.objects.all()


class WorkAPIUpdateView(generics.UpdateAPIView):
    serializer_class = WorkSerializer
    queryset = Work.objects.all()

