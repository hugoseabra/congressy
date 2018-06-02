from django.http import JsonResponse
from rest_framework import viewsets
from datetime import datetime
from scientific_work import forms
from scientific_work.models import Work, Author, AreaCategory, WorkConfig
from scientific_work.serializers import WorkSerializer, AuthorSerializer, \
    AreaCategorySerializer, WorkConfigSerializer


class WorkViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Works to be viewed or edited.
    """
    queryset = Work.objects.all()
    serializer_class = WorkSerializer


class AuthorViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Authors to be viewed or edited.
    """
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer


class AreaCategoryViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows AreaCategories to be viewed or edited.
    """
    queryset = AreaCategory.objects.all()
    serializer_class = AreaCategorySerializer


class WorkConfigViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows WorkConfigs to be viewed or edited.
    """
    queryset = WorkConfig.objects.all()
    serializer_class = WorkConfigSerializer

    def update(self, request, *args, **kwargs):
        if 'date_start_0' in request.data and 'date_start_1':
            request.POST._mutable = True
            full_date = request.data['date_start_0'] + ' ' + request.data[
                'date_start_1']

            start = datetime.strptime(full_date, '%d/%m/%Y %H:%M')
            request.data['date_start'] = start

        if 'date_end_0' in request.data and 'date_end_1':
            request.POST._mutable = True
            full_date = request.data['date_end_0'] + ' ' + request.data[
                'date_end_1']

            end = datetime.strptime(full_date, '%d/%m/%Y %H:%M')
            request.data['date_end'] = end

        return super().update(request, *args, **kwargs)
