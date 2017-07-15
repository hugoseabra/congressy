"""
Deletable model mixin
"""

from django.db import IntegrityError, models, router
from django.db.models.deletion import Collector


class NotDeletableError(IntegrityError):
    """Not deletable exception"""

    def __init__(self, *args, **kwargs):
        super(NotDeletableError, self).__init__(
            'Você não pode excluir este registro.',
            * args,
            **kwargs
        )


class CheckerCollector(Collector):
    """Collection checker for deletable model"""
    def __init__(self, *args, **kwargs):
        super(CheckerCollector, self).__init__(*args, **kwargs)
        self.protected = set()

    def collect(self, objs, **kwargs):
        """ @see super(CheckerCollector, self).collect """
        try:
            return super(CheckerCollector, self).collect(objs, **kwargs)

        except models.ProtectedError as exc:
            self.protected.update(exc.protected_objects)

    def can_fast_delete(self, objs, from_field=None):
        """
        We always want to load the objects into memory so that we can display
        them to the user in confirm page.
        """
        return False


class DeletableModelMixin(object):
    """Deletable model checker"""
    checker = None

    def is_deletable(self):
        """Checks if model is deletable"""
        if not self.checker:
            self.checker = CheckerCollector(using=router.db_for_write(self))

        self.checker.collect(objs=[self])
        return len(self.checker.protected) == 0

    def check_deletable(self):
        """Raises an exception if model is not deletable"""

        if self.is_deletable() is False:
            raise NotDeletableError()
