from django.http import JsonResponse
from rest_framework import viewsets

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
    API endpoint that allows AreaCategories to be viewed or edited.
    """
    queryset = WorkConfig.objects.all()
    serializer_class = WorkConfigSerializer

    def update(self, request, *args, **kwargs):
        request.POST._mutable = True
        instance = self.get_instance(request.data)
        if 'date_start_0' not in request.data:
            request.data['date_start_0'] = instance.date_start.strftime(
                '%e/%m/%Y')
            request.data['date_start_1'] = instance.date_start.strftime(
                '%H:%M')

        if 'date_end_0' not in request.data:
            request.data['date_end_0'] = instance.date_end.strftime(
                '%e/%m/%Y')
            request.data['date_end_1'] = instance.date_end.strftime('%H:%M')

        model_form = forms.WorkConfigForm(instance=instance, data=request.data)
        if model_form.is_valid():
            saved = model_form.save()
            serializer_instance = WorkConfigSerializer(instance=saved,
                                                       data=request.data)
            if serializer_instance.is_valid():
                data = serializer_instance.data
                return JsonResponse(data, status=201)
            else:
                return JsonResponse({'errors': serializer_instance.errors},
                                    status=400)
        else:
            return JsonResponse({'errors': model_form.errors}, status=400)

    @staticmethod
    def get_instance(data):
        return WorkConfig.objects.get(event=data.get('event'))
