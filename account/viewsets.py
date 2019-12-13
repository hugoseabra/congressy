from rest_framework import generics, viewsets
from rest_framework.permissions import AllowAny

from account.serializers import AccountSerializer


class AccountCreateViewset(generics.CreateAPIView, viewsets.GenericViewSet):
    serializer_class = AccountSerializer
    permission_classes = (
        AllowAny,
    )

    def perform_create(self, serializer):
        serializer.create(request=self.request)
