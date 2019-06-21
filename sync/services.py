from base.services import ApplicationService
from sync import managers


class SyncClientService(ApplicationService):
    manager_class = managers.SyncClientManager


class SyncQueueService(ApplicationService):
    manager_class = managers.SyncQueueManager
