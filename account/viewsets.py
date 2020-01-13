from rest_framework import generics, viewsets

from account.serializers import AccountSerializer


class AccountCreateViewset(generics.CreateAPIView, viewsets.GenericViewSet):
    serializer_class = AccountSerializer

    def perform_create(self, serializer):
        serializer.save(request=self.request)
