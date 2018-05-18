from rest_framework import viewsets
from django.http import HttpResponse, JsonResponse

from scientific_work.models import Work, Author, AreaCategory, WorkConfig
from scientific_work.serializers import WorkSerializer, AuthorSerializer, \
    AreaCategorySerializer, WorkConfigSerializer

from scientific_work import forms


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

    def update(self, request, *args, **kwargs):
        instance = self.get_instance(request.data)
        model_form = forms.WorkConfigForm(instance=instance, data=request.data)
        if model_form.is_valid():
            data = WorkConfigSerializer(instance=model_form.instance).data
            return JsonResponse(data, status=201)
        else:
            return JsonResponse({'errors': model_form.errors}, status=400)

    def get_instance(self, data):
        return WorkConfig.objects.get(event=data.get('event'))
