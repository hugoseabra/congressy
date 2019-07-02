import hashlib
import os

from django.db.transaction import atomic

from base.managers import Manager
from sync.models import SyncClient, SyncQueue


class SyncClientManager(Manager):
    class Meta:
        model = SyncClient
        fields = (
            'event',
            'name',
            'active',
        )

    def save(self, commit=True):
        if not self.instance.key:
            self.instance.key = hashlib.md5(os.urandom(32)).hexdigest()

        return super().save(commit)


class SyncQueueManager(Manager):
    class Meta:
        model = SyncQueue
        fields = '__all__'

    def save(self, commit=True):
        with atomic():
            try:
                instance = super().save(commit)

                # After save because of file persistence
                instance.validate()
                instance.save()

            except Exception as e:
                instance.file_path.delete()
                raise Exception(str(e))

        return instance
