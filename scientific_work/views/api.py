from rest_framework import generics, exceptions

from scientific_work.serializers import WorkSerializer
from scientific_work.models import Work


class WorkAPIListView(generics.ListAPIView):
    serializer_class = WorkSerializer
    queryset = Work.objects.all()

    def get_queryset(self):
        queryset = super().get_queryset()
        allowed = []
        user = self.request.user
        for work in queryset:
            if work.subscription.person.user == user:
                allowed.append(work)
        return allowed


class WorkAPIUpdateView(generics.RetrieveUpdateAPIView):
    serializer_class = WorkSerializer
    queryset = Work.objects.all()

    def get_serializer(self, *args, **kwargs):
        kwargs['partial'] = True
        return super().get_serializer(*args, **kwargs)

    def get_object(self):
        work = super().get_object()
        user = self.request.user
        if work.subscription.person.user != user:
            raise exceptions.PermissionDenied
        return work

