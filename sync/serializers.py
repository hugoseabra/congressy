from rest_framework import serializers

from core.serializers import FormSerializerMixin
from sync.models import SyncClient, SyncQueue
from sync.services import SyncClientService, SyncQueueService


class SyncClientSerializer(FormSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = SyncClient
        form = SyncClientService
        fields = '__all__'


class SyncQueueSerializer(FormSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = SyncQueue
        form = SyncQueueService
        fields = '__all__'
