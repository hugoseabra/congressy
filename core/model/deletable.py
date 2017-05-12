from django.db import IntegrityError, models, router
from django.db.models.deletion import Collector


class NotDeletableError(IntegrityError):
    def __init__(self, *args, **kwargs):
        super(NotDeletableError, self).__init__(
            'Você não pode excluir este registro.',
            * args,
            **kwargs
        )


class CheckerCollector(Collector):
    def __init__(self, *args, **kwargs):
        super(CheckerCollector, self).__init__(*args, **kwargs)
        self.protected = set()

    def collect(self, objs, **kwargs):
        try:
            return super(CheckerCollector, self).collect(objs, **kwargs)
        except models.ProtectedError as e:
            self.protected.update(e.protected_objects)

    def can_fast_delete(self, objs, from_field=None):
        """
        We always want to load the objects into memory so that we can display
        them to the user in confirm page.
        """
        return False


class DeletableModel(object):
    def __init__(self):
        self.checker = CheckerCollector(using=router.db_for_write(self))

    def is_deletable(self):
        self.checker.collect(objs=[self])
        return len(self.checker.protected) == 0

    def check_deletable(self):
        if self.is_deletable() is False:
            raise NotDeletableError()
