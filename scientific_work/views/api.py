from rest_framework import viewsets

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
    API endpoint that allows AreaCategories to be viewed or edited.
    """
    queryset = WorkConfig.objects.all()
    serializer_class = WorkConfigSerializer
