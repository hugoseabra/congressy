from rest_framework import routers

from sync import viewsets

router = routers.DefaultRouter()
router.register(r'sync/clients',
                viewsets.SyncClientViewSet,
                base_name="sync_client", )

router.register(r'sync/queues',
                viewsets.SyncQueueViewSet,
                base_name="sync_queue", )

urlpatterns = router.urls
