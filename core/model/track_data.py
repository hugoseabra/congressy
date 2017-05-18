"""Decorator @track_data - Tracks changes in models"""

from django.db.models.signals import post_init


# from https://gist.github.com/dcramer/730765
def track_data(*fields):
    """
    Tracks property changes on a model instance.
    The changed list of properties is refreshed on model initialization
    and save.

    @track_data('name')
    class Post(models.Model):
        name = models.CharField(...)
        @classmethod
        def post_save(cls, sender, instance, created, **kwargs):
            if instance.has_changed('name'):
                print "Hooray!"
    """

    not_saved = dict()

    def _store(self):
        """Updates a local copy of attributes values"""
        if self.pk:
            self.data = dict((f, getattr(self, f)) for f in fields)
        else:
            self.data = not_saved

    def inner(cls):
        """Inner callback to return"""

        # contains a local copy of the previous values of attributes
        cls.data = {}

        def has_changed(self, field):
            """Returns `True` if `field` has changed since initialization."""
            if self.data is not_saved:
                return False
            return self.data.get(field) != getattr(self, field)

        cls.has_changed = has_changed

        def old_value(self, field):
            """Returns the previous value of `field`"""
            return self.data.get(field)

        cls.old_value = old_value

        def whats_changed(self):
            """Returns a list of changed attributes."""
            changed = {}
            if self.data is not_saved:
                return changed
            for key, value in self.data.items():
                if value != getattr(self, key):
                    changed[key] = value
            return changed

        cls.whats_changed = whats_changed

        # Ensure we are updating local attributes on model init
        def _post_init(instance, **kwargs):
            _store(instance)

        post_init.connect(_post_init, sender=cls, weak=False)

        # Ensure we are updating local attributes on model save
        def save(self, *args, **kwargs):
            """Intercepts save() in post_init signal"""

            save.original(self, *args, **kwargs)
            _store(self)

        save.original = cls.save
        cls.save = save
        return cls

    return inner
